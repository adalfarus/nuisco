import base64

with open('_socket.pyd', 'rb') as f:
    binary_data = f.read()

base64_encoded = base64.b64encode(binary_data).decode('utf-8')

with open('output.py', 'w') as f:
    f.write(f'data = "{base64_encoded}"\n')
