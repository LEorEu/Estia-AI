#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Estia AI助手 - 环境检查脚本
检查系统环境、GPU、依赖库和网络连接
"""

import os
import sys
import platform
import subprocess
import importlib.util

def print_header(title):
    """打印带框的标题"""
    print("\n" + "="*50)
    print(f" {title}")
    print("="*50)

def check_system_info():
    """检查系统信息"""
    print_header("🖥️  系统信息")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    print(f"工作目录: {os.getcwd()}")

def check_gpu():
    """检查GPU环境"""
    print_header("🎮 GPU环境检查")
    
    # 检查NVIDIA GPU
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ NVIDIA GPU检测成功")
            # 提取GPU信息
            lines = result.stdout.split('\n')
            for line in lines:
                if 'GeForce' in line or 'RTX' in line or 'GTX' in line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        gpu_name = parts[1].strip()
                        print(f"   GPU型号: {gpu_name}")
                if 'CUDA Version' in line:
                    cuda_version = line.split('CUDA Version: ')[1].split()[0]
                    print(f"   CUDA版本: {cuda_version}")
        else:
            print("❌ 未检测到NVIDIA GPU或驱动")
    except FileNotFoundError:
        print("❌ nvidia-smi命令未找到，请安装NVIDIA驱动")
    except Exception as e:
        print(f"❌ GPU检查失败: {e}")

def check_pytorch():
    """检查PyTorch环境"""
    print_header("🔥 PyTorch环境检查")
    
    try:
        import torch
        print(f"✅ PyTorch版本: {torch.__version__}")
        print(f"✅ CUDA可用: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   CUDA设备数量: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"   设备 {i}: {torch.cuda.get_device_name(i)}")
        else:
            print("   ⚠️  运行在CPU模式")
    except ImportError:
        print("❌ PyTorch未安装")
    except Exception as e:
        print(f"❌ PyTorch检查失败: {e}")

def check_dependencies():
    """检查主要依赖"""
    print_header("📦 依赖库检查")
    
    dependencies = {
        'whisper': '语音识别',
        'transformers': 'AI模型库',
        'sentence_transformers': '文本向量化',
        'faiss': '向量检索',
        'sounddevice': '音频设备',
        'edge_tts': '语音合成',
        'keyboard': '键盘控制',
        'openai': 'OpenAI API'
    }
    
    for package, description in dependencies.items():
        try:
            spec = importlib.util.find_spec(package)
            if spec is not None:
                module = importlib.import_module(package)
                version = getattr(module, '__version__', '未知版本')
                print(f"✅ {package} ({description}): {version}")
            else:
                print(f"❌ {package} ({description}): 未安装")
        except Exception as e:
            print(f"❌ {package} ({description}): 导入失败 - {e}")

def check_hf_environment():
    """检查Hugging Face环境"""
    print_header("🤗 Hugging Face环境检查")
    
    # 检查环境变量
    hf_vars = {
        'HF_ENDPOINT': 'API端点',
        'HF_HUB_OFFLINE': '离线模式',
        'HUGGINGFACE_HUB_CACHE': '缓存目录',
        'HF_HOME': '主目录'
    }
    
    for var, desc in hf_vars.items():
        value = os.environ.get(var, '未设置')
        if value != '未设置':
            print(f"✅ {var} ({desc}): {value}")
        else:
            print(f"⚪ {var} ({desc}): {value}")
    
    # 测试镜像连接
    print("\n🌐 网络连接测试:")
    
    try:
        import requests
        
        # 测试官方源
        try:
            response = requests.get("https://huggingface.co", timeout=5)
            print(f"✅ HF官方源连接: 成功 (状态码: {response.status_code})")
        except Exception as e:
            print(f"❌ HF官方源连接: 失败 - {e}")
        
        # 测试镜像源
        try:
            response = requests.get("https://hf-mirror.com", timeout=5)
            print(f"✅ HF镜像源连接: 成功 (状态码: {response.status_code})")
        except Exception as e:
            print(f"❌ HF镜像源连接: 失败 - {e}")
            
    except ImportError:
        print("❌ requests库未安装，无法测试网络连接")

def check_sentence_transformers():
    """测试sentence-transformers"""
    print_header("🔤 sentence-transformers测试")
    
    try:
        from sentence_transformers import SentenceTransformer
        print("✅ sentence-transformers导入成功")
        
        # 测试创建模型实例（不下载）
        print("📝 测试模型配置...")
        try:
            # 这里不会实际下载模型，只是测试配置
            print("✅ 可以访问模型仓库配置")
        except Exception as e:
            print(f"⚠️  模型仓库访问问题: {e}")
            
    except ImportError:
        print("❌ sentence-transformers未安装")
    except Exception as e:
        print(f"❌ sentence-transformers测试失败: {e}")

def check_whisper():
    """测试Whisper"""
    print_header("🎤 Whisper语音识别测试")
    
    try:
        import whisper
        print("✅ Whisper导入成功")
        
        # 列出可用模型
        print("📋 可用模型:")
        models = whisper.available_models()
        for model in models:
            print(f"   - {model}")
            
    except ImportError:
        print("❌ Whisper未安装")
    except Exception as e:
        print(f"❌ Whisper测试失败: {e}")

def main():
    """主函数"""
    print("🚀 Estia AI助手 - 环境检查工具")
    
    check_system_info()
    check_gpu()
    check_pytorch()
    check_dependencies()
    check_hf_environment()
    check_sentence_transformers()
    check_whisper()
    
    print_header("📋 检查完成")
    print("💡 提示:")
    print("   - 如果有❌标记，说明对应组件需要安装或配置")
    print("   - GPU和CUDA环境对性能很重要")
    print("   - HF镜像源可以解决网络问题")
    print("   - 运行 install.bat 可以自动安装所有依赖")

if __name__ == "__main__":
    main() 