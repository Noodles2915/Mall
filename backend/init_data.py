#!/usr/bin/env python
"""
初始化数据脚本
用于快速创建测试数据
"""

import os
import sys
import django
from decimal import Decimal

# 设置 Django 设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mall.settings')
django.setup()

from django.contrib.auth import get_user_model
from product.models import ProductCategory, Product
from user.models import Address

User = get_user_model()


def create_test_users():
    """创建测试用户"""
    print("创建测试用户...")
    
    test_users = [
        {'username': 'alice', 'email': 'alice@example.com', 'password': '123456'},
        {'username': 'bob', 'email': 'bob@example.com', 'password': '123456'},
        {'username': 'charlie', 'email': 'charlie@example.com', 'password': '123456'},
    ]
    
    for user_data in test_users:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
            }
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f"  ✓ 创建用户: {user.username}")
        else:
            print(f"  - 用户已存在: {user.username}")


def create_test_addresses():
    """创建测试收货地址"""
    print("\n创建测试地址...")
    
    user = User.objects.filter(username='alice').first()
    if not user:
        print("  ✗ alice 用户不存在")
        return
    
    addresses = [
        {
            'name': '张三',
            'phone': '13800138000',
            'province': '广东省',
            'city': '深圳市',
            'district': '南山区',
            'detail': '科技园 1 号',
            'is_default': True,
        },
        {
            'name': '李四',
            'phone': '13900139000',
            'province': '北京市',
            'city': '北京市',
            'district': '海淀区',
            'detail': '中关村大街 100 号',
            'is_default': False,
        },
    ]
    
    for addr_data in addresses:
        address, created = Address.objects.get_or_create(
            user=user,
            detail=addr_data['detail'],
            defaults=addr_data
        )
        if created:
            print(f"  ✓ 创建地址: {address.name} ({address.detail})")
        else:
            print(f"  - 地址已存在: {address.name}")


def create_test_categories():
    """创建测试分类"""
    print("\n创建测试分类...")
    
    categories = [
        {'name': '数码电器', 'parent': None, 'sort': 10},
        {'name': '手机', 'parent_name': '数码电器', 'sort': 11},
        {'name': '平板', 'parent_name': '数码电器', 'sort': 12},
        {'name': '服装', 'parent': None, 'sort': 20},
        {'name': '男装', 'parent_name': '服装', 'sort': 21},
        {'name': '女装', 'parent_name': '服装', 'sort': 22},
    ]
    
    for cat_data in categories:
        parent = None
        if 'parent_name' in cat_data:
            parent = ProductCategory.objects.filter(
                name=cat_data['parent_name']
            ).first()
        
        category, created = ProductCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'parent': parent,
                'sort': cat_data.get('sort', 0),
                'is_active': True,
            }
        )
        if created:
            print(f"  ✓ 创建分类: {category.name}")
        else:
            print(f"  - 分类已存在: {category.name}")


def create_test_products():
    """创建测试商品"""
    print("\n创建测试商品...")
    
    phone_category = ProductCategory.objects.filter(name='手机').first()
    if not phone_category:
        print("  ✗ 手机分类不存在")
        return
    
    products = [
        {
            'name': 'Aster X1 Pro 手机',
            'subtitle': '2K屏/5000mAh/快充',
            'price': Decimal('3299.00'),
            'stock': 120,
            'is_hot': True,
            'description': '旗舰性能与长续航兼顾的全能机型。骁龙8 Gen 3 处理器，2K 屏幕，5000mAh 大电池。',
            'specs': {
                '颜色': ['曜石黑', '冰川蓝', '星云紫'],
                '内存': ['12GB+256GB', '16GB+512GB'],
            },
        },
        {
            'name': 'Aster Lite 手机',
            'subtitle': '高刷屏/大电池/平价',
            'price': Decimal('1999.00'),
            'stock': 200,
            'is_hot': True,
            'description': '性价比之选，配备高刷屏和大电池，适合日常使用。',
            'specs': {
                '颜色': ['午夜黑', '雪山白'],
                '内存': ['6GB+128GB', '8GB+256GB'],
            },
        },
        {
            'name': 'Aster Ultra Max 手机',
            'subtitle': '最强拍照/超长续航',
            'price': Decimal('5999.00'),
            'stock': 50,
            'is_hot': False,
            'description': '顶级旗舰，配备最强相机系统和超长续航能力。',
            'specs': {
                '颜色': ['钛金黑', '白金', '金色'],
                '内存': ['16GB+512GB', '16GB+1TB'],
            },
        },
        {
            'name': '手机壳（Aster X1 Pro）',
            'subtitle': '防粗鲁/防摔/防水',
            'price': Decimal('69.90'),
            'stock': 500,
            'is_hot': False,
            'description': '专为 Aster X1 Pro 设计的高级保护壳。',
            'specs': {
                '颜色': ['黑色', '蓝色', '红色'],
                '材质': ['硅胶', '皮革'],
            },
        },
        {
            'name': '高速充电器 65W',
            'subtitle': '快速充电/多协议',
            'price': Decimal('129.00'),
            'stock': 300,
            'is_hot': False,
            'description': '支持 PD、QC、AFC 等多种快速充电协议。',
            'specs': {
                '功率': ['65W', '100W'],
                '输出': ['单口', '双口'],
            },
        },
    ]
    
    for prod_data in products:
        product, created = Product.objects.get_or_create(
            name=prod_data['name'],
            category=phone_category,
            defaults={
                'subtitle': prod_data['subtitle'],
                'price': prod_data['price'],
                'stock': prod_data['stock'],
                'is_hot': prod_data['is_hot'],
                'description': prod_data['description'],
                'specs': prod_data['specs'],
                'cover_url': 'https://picsum.photos/id/1/800/800',
                'is_active': True,
            }
        )
        if created:
            print(f"  ✓ 创建商品: {product.name}")
        else:
            print(f"  - 商品已存在: {product.name}")


def main():
    """主函数"""
    print("=" * 50)
    print("电商平台 - 初始化数据")
    print("=" * 50)
    
    try:
        create_test_users()
        create_test_addresses()
        create_test_categories()
        create_test_products()
        
        print("\n" + "=" * 50)
        print("✓ 数据初始化完成！")
        print("=" * 50)
        print("\n测试账户信息：")
        print("  用户名: alice     密码: 123456")
        print("  用户名: bob       密码: 123456")
        print("  用户名: charlie   密码: 123456")
        print("\n后台访问地址: http://localhost:8000/admin/")
        print("API 基础 URL: http://localhost:8000/api/")
        
    except Exception as e:
        print(f"\n✗ 初始化失败: {str(e)}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
