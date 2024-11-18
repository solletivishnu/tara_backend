from .default import *

DEBUG = True
DATABASES = {
        'default': {
            'ENGINE': 'djongo',
            'NAME': 'development',
            'ENFORCE_SCHEMA': False,
            'CLIENT': {
                'host': 'mongodb+srv://dev-user:4b1nZ9uMSsBR8ccY@cluster0.vxfiacn.mongodb.net/development'
                        '?tls=true&tlsAllowInvalidCertificates=true',
                'port': 27017,
                'username': 'dev-user',
                'password': '4b1nZ9uMSsBR8ccY',
                'authSource': 'db-dev',
                'authMechanism': 'SCRAM-SHA-1',
                'tls': True,
                'tlsAllowInvalidCertificates': True
            },
            'CONN_MAX_AGE': None
        }
}

