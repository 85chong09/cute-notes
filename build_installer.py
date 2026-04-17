import os
import sys
import subprocess
import shutil

def build_installer():
    print("=" * 50)
    print("开始构建可爱便签安装包...")
    print("=" * 50)
    
    # 检查是否安装了PyInstaller
    try:
        import PyInstaller
        print("✓ PyInstaller已安装")
    except ImportError:
        print("正在安装PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller安装成功")
    
    # 构建命令
    build_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=可爱便签",
        "--windowed",
        "--onefile",
        "--clean",
        "--add-data", "config.py" + os.pathsep + ".",
        "main.py"
    ]
    
    print("\n正在构建可执行文件...")
    result = subprocess.run(build_cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"构建失败: {result.stderr}")
        return False
    
    print("✓ 可执行文件构建成功")
    
    # 检查输出文件
    dist_dir = os.path.join(os.getcwd(), "dist")
    exe_file = os.path.join(dist_dir, "可爱便签.exe")
    
    if os.path.exists(exe_file):
        print(f"\n✓ 安装包已生成: {exe_file}")
        print(f"  文件大小: {os.path.getsize(exe_file) / 1024 / 1024:.2f} MB")
        
        # 清理临时文件
        build_dir = os.path.join(os.getcwd(), "build")
        spec_file = os.path.join(os.getcwd(), "可爱便签.spec")
        
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        if os.path.exists(spec_file):
            os.remove(spec_file)
        
        print("\n✓ 临时文件已清理")
        print("\n" + "=" * 50)
        print("构建完成！")
        print(f"可执行文件位置: {exe_file}")
        print("=" * 50)
        return True
    else:
        print("✗ 构建失败，未找到可执行文件")
        return False

if __name__ == "__main__":
    build_installer()
