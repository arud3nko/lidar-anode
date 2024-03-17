import asyncio
import uuid


async def scan_imitation(writer):
    while True:
        await asyncio.sleep(0.001)
        writer.write(str(uuid.uuid4()).encode())
        await writer.drain()  # Обязательно использовать await writer.drain() для гарантии отправки данных


async def handle_connection(reader, writer):
    addr = writer.get_extra_info("peername")
    print("Connected by", addr)

    scanning_task = None  # Ссылка на задачу сканирования

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            data = data.upper()
            print(f"Received from {addr}: {data}")

            if data.startswith(b'\x02\x02\x02\x02\x00\x00\x00\x10'):
                print("Starting scanning...")
                if scanning_task is None or scanning_task.done():  # Проверяем, что задача сканирования не запущена или уже завершена
                    scanning_task = asyncio.create_task(scan_imitation(writer))  # Запускаем задачу сканирования
                else:
                    print("Scanning is already running")

            elif data.startswith(b'\x02\x02\x02\x02\x00\x00\x00\x11'):
                print("Stopping scanning...")
                if scanning_task is not None and not scanning_task.done():  # Проверяем, что задача сканирования запущена и не завершена
                    scanning_task.cancel()  # Отменяем задачу сканирования
                else:
                    print("Scanning is not running")

    except asyncio.CancelledError:
        print("Scan imitation task cancelled")  # Сообщаем о том, что задача сканирования была отменена
    except ConnectionError:
        print(f"Client suddenly closed while receiving from {addr}")

    finally:
        print("Disconnected by", addr)
        writer.close()


async def main(host, port):
    server = await asyncio.start_server(handle_connection, host, port)
    async with server:
        await server.serve_forever()


HOST, PORT = "", 50007

if __name__ == "__main__":
    asyncio.run(main(HOST, PORT))
