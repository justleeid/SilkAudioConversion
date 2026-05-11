#!/usr/bin/env python3
"""
创建测试 SILK 文件
用于测试转换功能
"""
import struct
import os

def create_standard_silk(output_path):
    """创建标准 SILK 文件（带结尾标记）"""
    # SILK 文件头
    header = b'#!silk_v3'
    
    # 创建一些模拟的 SILK 帧（简化版本）
    # 实际 SILK 帧结构更复杂，这里仅用于测试
    frames = b''
    for i in range(10):
        # 帧长度（20ms 帧）
        frame_len = struct.pack('<H', 100 + i)
        # 模拟帧数据
        frame_data = bytes([0x00] * (100 + i))
        frames += frame_len + frame_data
    
    # 结尾标记
    footer = b'\xff\xff'
    
    # 组合
    silk_data = header + frames + footer
    
    with open(output_path, 'wb') as f:
        f.write(silk_data)
    
    print(f"创建标准 SILK 文件: {output_path}")
    print(f"   大小: {len(silk_data)} bytes")

def create_wechat_silk(output_path):
    """创建微信 SILK 文件（带 0x02 头，无结尾标记）"""
    # 微信文件头
    wechat_header = b'\x02#!silk_v3'
    
    # 创建模拟帧
    frames = b''
    for i in range(10):
        frame_len = struct.pack('<H', 100 + i)
        frame_data = bytes([0x00] * (100 + i))
        frames += frame_len + frame_data
    
    # 微信 SILK 无结尾标记
    silk_data = wechat_header + frames
    
    with open(output_path, 'wb') as f:
        f.write(silk_data)
    
    print(f"创建微信 SILK 文件: {output_path}")
    print(f"   大小: {len(silk_data)} bytes")

if __name__ == '__main__':
    fixtures_dir = os.path.dirname(__file__)
    
    # 创建测试文件
    create_standard_silk(os.path.join(fixtures_dir, 'test_standard.silk'))
    create_wechat_silk(os.path.join(fixtures_dir, 'test_wechat.silk'))
    
    print("\n测试文件创建完成！")
