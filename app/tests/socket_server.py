"""

Тестовый сокет-сервер, отправляет сообщения, имитируя лидар.
Считывает сообщения в виде байтов из txt-файла с тестовыми данными.
При этом реагирует на команды запуска/останова.

Запустить для тестов, перед запуском ПС

"""

import asyncio
import aiofiles


async def scan_imitation(writer):
    async with aiofiles.open("data/source_data_bytes.txt", "rb") as file:
        while True:
            data = await file.read(3489)
            if not data:  # Если данных больше нет, выходим из цикла
                break
            await asyncio.sleep(0.001)
            writer.write(data)
            await writer.drain()


async def scan_imitation_hex(writer):
    async with aiofiles.open("data/dataset_clean.txt", "r") as file:
        while True:
            data = await file.read(6978)
            if not data:  # Если данных больше нет, выходим из цикла
                break
            await asyncio.sleep(0.001)
            writer.write(data)
            await writer.drain()


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
                if scanning_task is None or scanning_task.done():
                    scanning_task = asyncio.create_task(scan_imitation(writer))  # Запускаем задачу сканирования
                else:
                    print("Scanning is already running")

            elif data.startswith(b'\x02\x02\x02\x02\x00\x00\x00\x11'):
                print("Stopping scanning...")
                if scanning_task is not None and not scanning_task.done():
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
