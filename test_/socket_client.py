import asyncio


async def tcp_client(host, port, message):
    reader, writer = await asyncio.open_connection(host, port)

    print(f'Connected to {host}:{port}')

    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(1024)
    print(f'Received: {data.decode()}')

    print('Closing connection')
    writer.close()
    await writer.wait_closed()


async def main():
    host1 = '127.0.0.1'  # Host of the first socket
    port1 = 50007         # Port of the first socket
    message1 = 'Hello from socket 1'

    host2 = '127.0.0.1'  # Host of the second socket
    port2 = 50007         # Port of the second socket
    message2 = 'Hello from socket 2'

    await asyncio.gather(
        tcp_client(host1, port1, message1),
        tcp_client(host2, port2, message2)
    )

asyncio.run(main())
