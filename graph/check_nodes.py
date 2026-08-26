from nodes.tool import response_node
import asyncio

while True:
    
    data = asyncio.run(response_node())
    print(data)


