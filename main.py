import asyncio
import aiofiles

from contextlib import suppress
from asyncio import Queue


from app.carriage import Carriage
from app.lidar import Lidar, LidarParams


async def simple_test_carriage(carriage: Carriage):
    async for stage in carriage.move():
        print(stage)


async def carriage_imitation(*args):
    for stage in ["started", "moved", "stopped", "started", "moved", "stopped", "returned"]:
        print(f">>> Каретка на этапе: {stage.upper()}")
        await asyncio.sleep(1)
        if stage == "returned":
            for task in args:
                task.cancel()


async def lidar_worker(number: int, ip: str, message_queue: Queue):
    lidar_params = LidarParams(ip=ip,
                               port=50007)

    async with Lidar(params=lidar_params) as lidar:
        async for message in await lidar.scan():
            print(f"> Lidar #{number} {message}")
            await message_queue.put((number, message))


async def process_messages(message_queue: asyncio.Queue, file_path: str):
    async with aiofiles.open(file_path, 'ab') as file:
        while True:
            try:
                number, message = await asyncio.wait_for(message_queue.get(), timeout=0.1)
            except asyncio.TimeoutError:
                break
            await file.write(message)


async def scan_anode():
    message_queue = asyncio.Queue()
    file_path = "./lidar_messages.txt"  # Путь к файлу для записи сообщений

    lidar_task_1 = asyncio.create_task(lidar_worker(1, "", message_queue))
    lidar_task_2 = asyncio.create_task(lidar_worker(2, "", message_queue))

    carriage_move_task = asyncio.create_task(carriage_imitation(lidar_task_1, lidar_task_2))
    message_processing_task = asyncio.create_task(process_messages(message_queue, file_path))

    with suppress(asyncio.CancelledError):
        await lidar_task_1
        await lidar_task_2

    await carriage_move_task
    await message_processing_task


async def main():
    await scan_anode()


if __name__ == '__main__':
    asyncio.run(main())
