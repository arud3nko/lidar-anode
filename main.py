import asyncio

from contextlib import suppress

from app.constants import MoveStages
from app.carriage.carriage import Carriage
from app.lidar.lidar import Lidar


async def simple_test_carriage(carriage: Carriage):
    async for stage in carriage.move():
        print(stage)


async def test_carriage(carriage: Carriage, *args):
    async for stage in carriage.move():
        print(stage)
        if stage == MoveStages.MOVED.value:
            for task in args:
                task.cancel()


async def test_lidar(lidar: Lidar):
    async for data in lidar.scan():
        print(f"[Lidar {lidar.ip}] {data}")


async def main():
    carriage = Carriage()
    lidar1 = Lidar(ip="1")
    lidar2 = Lidar(ip="2")

    lidar_task_1 = asyncio.create_task(test_lidar(lidar1))
    lidar_task_2 = asyncio.create_task(test_lidar(lidar2))

    carriage_move_task = asyncio.create_task(test_carriage(carriage,
                                                           lidar_task_1,
                                                           lidar_task_2
                                                           ))

    async with suppress(asyncio.CancelledError):
        await lidar_task_1
        await lidar_task_2

    await carriage_move_task


if __name__ == '__main__':
    asyncio.run(main())