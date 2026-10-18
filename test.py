from tools import select_tool
question = 'tell me about leave policies'
tool = select_tool('query_generator_tool')
print(tool)