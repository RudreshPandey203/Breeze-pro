# response_from_gpt = ```json{"1":"step1", "2":"step2"}```

# # Find the index of the opening and closing curly braces
# opening_index = response_from_gpt.find('{')
# closing_index = response_from_gpt.rfind('}')

# # Extract the substring between the opening and closing curly braces
# stripped_response = response_from_gpt[opening_index:closing_index+1]

# print(stripped_response)