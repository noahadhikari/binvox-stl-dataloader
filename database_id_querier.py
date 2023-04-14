import asyncio
from prisma import Prisma

import json



async def main() -> None:
    db = Prisma()
    await db.connect()

    # models = await db.model.find_many()

    # async def get_modelId_from_stlID(stlID: str):
    #     return await db.model.find_first(where={'stlId': stlID})

    # model = await get_modelId_from_stlID('1YkElT0POFyn9cVbOr2fNOWt9S_kiUPf6')
    
    async def get_map_to_modelId(offset: int = 0, limit: int = 100000):
        # return await db.model.find_many({select={'id': True, 'stlId': True, 'binvoxId': True},
        #                                  take=100})
        return await db.query_raw(f'SELECT id, stlId, binvoxId \
                                    FROM Model \
                                    LIMIT {limit} \
                                    OFFSET {offset}')
    
    offset = 0
    result = []
    id_data = await get_map_to_modelId(offset)
    while (id_data):
        result.extend(id_data)
        offset += 100000
    
    # write the resulting models to a json file
    with open('data/id_data.json', 'w') as f:
        json.dump(result, f, indent=2)

    await db.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
