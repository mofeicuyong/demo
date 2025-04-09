import boto3

s3 = boto3.client('s3')

# 设置参数
bucket_name = 'stock'
s3_key = 'apple_stock.csv'
local_file_path = 'apple_stock.csv'

# 下载文件
s3.download_file(bucket_name, s3_key, local_file_path)

print("✅ 文件下载完成！")
