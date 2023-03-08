import boto3

parameter_name = 'rpi-data-bucket-uri'

def get_parameter():
    client = boto3.client('ssm')
    full_bucket_uri = client.get_parameter(
        Name=parameter_name,
        WithDecryption=False
        )['Parameter']['Value']

    split_full_butcket_uri = full_bucket_uri.split('/')
    # bucket_name = split_full_butcket_uri[2]
    # bucket_key = split_full_butcket_uri[3]

    # print(bucket_name, bucket_key)

    # return bucket_name, bucket_key
    print(split_full_butcket_uri[2], split_full_butcket_uri[3])

    return split_full_butcket_uri[2], split_full_butcket_uri[3]


