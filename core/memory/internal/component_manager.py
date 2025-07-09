#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
内部组件管理器
统一管理组件的初始化和生命周期，不对外暴露
"""

import logging
from typing import Dict, Any, Optional, List, Callable, Set
from .error_handler import ErrorHandlerMixin

logger = logging.getLogger(__name__)

class ComponentManager(ErrorHandlerMixin):
    """内部组件管理器 - 不对外暴露"""
    
    def __init__(self):
        super().__init__()
        self.components: Dict[str, Any] = {}
        self.initializers: Dict[str, Callable] = {}
        self.dependencies: Dict[str, List[str]] = {}
        self.component_configs: Dict[str, Dict[str, Any]] = {}
        self.initialized_components: Set[str] = set()
        self.initialization_order: List[str] = []
        self.initialization_in_progress: Set[str] = set()
        
        # 组件状态跟踪
        self.failed_components: Dict[str, str] = {}
        self.retry_counts: Dict[str, int] = {}
        self.max_retries = 3
    
    def register_component(self, 
                          name: str, 
                          initializer: Callable,
                          dependencies: List[str] = None,
                          config: Dict[str, Any] = None) -> None:
        """
        注册组件
        
        Args:
            name: 组件名称
            initializer: 初始化函数
            dependencies: 依赖的组件列表
            config: 组件配置
        """
        self.initializers[name] = initializer
        self.dependencies[name] = dependencies or []
        self.component_configs[name] = config or {}
        
        logger.debug(f"注册组件: {name}, 依赖: {dependencies}")
    
    def get_component(self, name: str, force_reinit: bool = False) -> Optional[Any]:
        """
        获取组件（懒加载）
        
        Args:
            name: 组件名称
            force_reinit: 是否强制重新初始化
            
        Returns:
            组件实例或None
        """
        if name in self.failed_components and not force_reinit:
            logger.warning(f"组件 {name} 之前初始化失败: {self.failed_components[name]}")
            return None
        
        if name not in self.components or force_reinit:
            success = self._initialize_component(name, force_reinit)
            if not success:
                return None
        
        return self.components.get(name)
    
    def _initialize_component(self, name: str, force_reinit: bool = False) -> bool:
        """
        初始化单个组件
        
        Args:
            name: 组件名称
            force_reinit: 是否强制重新初始化
            
        Returns:
            bool: 是否初始化成功
        """
        if name in self.initialization_in_progress:
            logger.error(f"检测到循环依赖: {name}")
            return False
        
        if name in self.initialized_components and not force_reinit:
            return True
        
        # 检查是否已达到最大重试次数
        if self.retry_counts.get(name, 0) >= self.max_retries:
            logger.error(f"组件 {name} 重试次数已达上限")
            return False
        
        self.initialization_in_progress.add(name)
        
        try:
            # 先初始化依赖组件
            for dep in self.dependencies.get(name, []):
                if not self._initialize_component(dep, force_reinit):
                    logger.error(f"组件 {name} 的依赖 {dep} 初始化失败")
                    self.initialization_in_progress.discard(name)
                    return False
            
            # 初始化组件
            initializer = self.initializers.get(name)
            if not initializer:
                logger.error(f"组件 {name} 没有初始化器")
                self.initialization_in_progress.discard(name)
                return False
            
            # 传递依赖组件给初始化器
            init_kwargs = self._prepare_init_kwargs(name)
            component = initializer(**init_kwargs)
            
            if component is None:
                logger.error(f"组件 {name} 初始化返回None")
                self.initialization_in_progress.discard(name)
                return False
            
            # 注册组件
            self.components[name] = component
            self.initialized_components.add(name)
            self.initialization_order.append(name)
            
            # 清除失败记录
            self.failed_components.pop(name, None)
            self.retry_counts.pop(name, None)
            
            logger.info(f"✅ 组件 {name} 初始化成功")
            return True
            
        except Exception as e:
            error_msg = f"组件 {name} 初始化失败: {e}"
            logger.error(error_msg)
            
            # 记录失败信息
            self.failed_components[name] = str(e)
            self.retry_counts[name] = self.retry_counts.get(name, 0) + 1
            
            return False
            
        finally:
            self.initialization_in_progress.discard(name)
    
    def _prepare_init_kwargs(self, name: str) -> Dict[str, Any]:
        """
        准备初始化参数
        
        Args:
            name: 组件名称
            
        Returns:
            Dict: 初始化参数
        """
        init_kwargs = {}
        
        # 添加依赖组件
        for dep in self.dependencies.get(name, []):
            dep_component = self.components.get(dep)
            if dep_component:
                init_kwargs[dep] = dep_component
        
        # 添加配置参数
        config = self.component_configs.get(name, {})
        init_kwargs.update(config)
        
        return init_kwargs
    
    def initialize_all(self) -> Dict[str, bool]:
        """
        初始化所有组件
        
        Returns:
            Dict: 组件名称到初始化结果的映射
        """
        results = {}
        
        for name in self.initializers:
            results[name] = self._initialize_component(name)
        
        logger.info(f"组件初始化完成: 成功 {sum(results.values())}/{len(results)}")
        return results
    
    def get_component_status(self) -> Dict[str, Any]:
        """
        获取组件状态
        
        Returns:
            Dict: 组件状态信息
        """
        return {
            'initialized_components': list(self.initialized_components),
            'failed_components': dict(self.failed_components),
            'initialization_order': self.initialization_order.copy(),
            'retry_counts': dict(self.retry_counts),
            'total_components': len(self.initializers),
            'success_rate': len(self.initialized_components) / len(self.initializers) if self.initializers else 0
        }
    
    def retry_failed_components(self) -> Dict[str, bool]:
        """
        重试失败的组件
        
        Returns:
            Dict: 重试结果
        """
        results = {}
        failed_names = list(self.failed_components.keys())
        
        for name in failed_names:
            logger.info(f"重试组件 {name}")
            results[name] = self._initialize_component(name, force_reinit=True)
        
        return results
    
    def shutdown_component(self, name: str) -> bool:
        """
        关闭单个组件
        
        Args:
            name: 组件名称
            
        Returns:
            bool: 是否关闭成功
        """
        if name not in self.components:
            return True
        
        try:
            component = self.components[name]
            
            # 如果组件有shutdown方法，调用它
            if hasattr(component, 'shutdown'):
                component.shutdown()
            elif hasattr(component, 'close'):
                component.close()
            
            # 从管理器中移除
            del self.components[name]
            self.initialized_components.discard(name)
            
            logger.info(f"✅ 组件 {name} 关闭成功")
            return True
            
        except Exception as e:
            logger.error(f"组件 {name} 关闭失败: {e}")
            return False
    
    def shutdown_all(self) -> Dict[str, bool]:
        """
        关闭所有组件
        
        Returns:
            Dict: 关闭结果
        """
        results = {}
        
        # 按照初始化顺序的逆序关闭
        for name in reversed(self.initialization_order):
            if name in self.components:
                results[name] = self.shutdown_component(name)
        
        # 清理状态
        self.components.clear()
        self.initialized_components.clear()
        self.initialization_order.clear()
        self.failed_components.clear()
        self.retry_counts.clear()
        
        logger.info("所有组件已关闭")
        return results
    
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """
        获取依赖关系图
        
        Returns:
            Dict: 依赖关系图
        """
        return self.dependencies.copy()
    
    def validate_dependencies(self) -> List[str]:
        """
        验证依赖关系
        
        Returns:
            List: 依赖问题列表
        """
        issues = []
        
        # 检查循环依赖
        def has_cycle(name: str, visited: Set[str], path: Set[str]) -> bool:
            if name in path:
                return True
            if name in visited:
                return False
            
            visited.add(name)
            path.add(name)
            
            for dep in self.dependencies.get(name, []):
                if has_cycle(dep, visited, path):
                    return True
            
            path.remove(name)
            return False
        
        visited = set()
        for name in self.initializers:
            if has_cycle(name, visited, set()):
                issues.append(f"检测到循环依赖: {name}")
        
        # 检查缺失的依赖
        for name, deps in self.dependencies.items():
            for dep in deps:
                if dep not in self.initializers:
                    issues.append(f"组件 {name} 依赖不存在的组件: {dep}")
        
        return issues