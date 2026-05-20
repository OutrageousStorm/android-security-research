#!/usr/bin/env python3
"""Fake Play Integrity API responses for testing"""
import json, base64, time

def create_fake_token():
    header = {'alg': 'HS256', 'typ': 'JWT'}
    payload = {
        'iss': 'https://play.googleapis.com',
        'aud': 'com.google.android.gms',
        'sub': '1234567890',
        'iat': int(time.time()),
        'exp': int(time.time()) + 3600,
        'requestDetails': {
            'nonce': 'test_nonce',
            'timestamp': int(time.time() * 1000),
        },
        'verdictDetails': {
            'appIntegrity': 'PLAY_RECOGNIZED',
            'deviceIntegrity': 'MEETS_DEVICE_INTEGRITY',
            'accountDetails': 'PLAY_EVALUATED',
        }
    }
    signature = 'fake_signature'
    return f"{json.dumps(header)}.{json.dumps(payload)}.{signature}"

print(create_fake_token())
