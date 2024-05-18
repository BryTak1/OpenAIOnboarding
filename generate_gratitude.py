from openai import OpenAI
import json
client = OpenAI()
example = "Write about a hobby you love and are grateful for I am really thankful for video games as a hobby. It has allowed me to still stay connected with my high school friends for all these years in college, even though we're far apart from each other during our respective quarters and semesters."
recip1 = "Online Gaming Communities"
reason1 = "for providing platforms where people can stay connected through shared interests in gaming, similar to how we stayed in touch with high school friends during college."
recip2 = "Video Game Developers and Companies"
reason2 = "for creating and maintaining the video games that have allowed us to connect with friends over long distances."

example2 = "What do you feel grateful for about Santa Cruz? The best thing about ucsc to me is the location and the nature of the campus. It seems every time that I'm on campus and stressed about anything, I can walk into the woods or take a hike or go mountain biking and forget about the stressful stuff for a bit."
recip3 = "Mountain Biking Groups and Clubs"
reason3 = "for organizing mountain biking activities and maintaining biking trails."
recip4 = "Outdoor Recreation Planners at UCSC"
reason4 = "for facilitating access to outdoor activities such as hiking and mountain biking."
messages = [{"role": "system", "content": "You are a helpful assistant designed to output JSON."}, {"role": "user", "content": 'Find the communities or groups that may have contributed to the what author is grateful for and describe why; Please do it in general groups or communities of people and do it in the format (we are thankful for ...); Also give two to three different groups: {example}'},{"role": "system", "content": f'We thank {recip1} {reason1} and {recip2} {reason2}'}]

def get_gratitude(post):
	if example in post:
		return json.dumps({recip1: reason1, recip2:reason2})
	elif example2 in post:
		return json.dumps({recip3: reason3, recip4:reason4})
	else:
		return json.dumps({"none":"none"})
def run_conversation():
	tools = [
	    {
		"type": "function",
		"function": {
			"name": "get_gratitude",
			"description": "Get the groups of people that contributed to what the author of the post was grateful for.",
			"parameters": {
				"type": "object",
				"properties": {
					"post": {
						"type": "string",
						"description": "The authors post describing what they are thankful for, e.g. What do you feel grateful for about Santa Cruz? the people i’ve met here! especially the fond memories i’ve made from hanging out, going on food adventures, and taking trips together to explore new cities."
					}},
				},
				"required": ["post"],
			},
		},
	]
	response = client.chat.completions.create(
		model="gpt-3.5-turbo-0125",
		messages=messages,
		response_format={"type": "json_object" },
		tools=tools,
		tool_choice="auto",
	)
	response_message = response.choices[0].message
	tool_calls = response_message.tool_calls
	if tool_calls:
		available_functions = {
			"get_gratitude": get_gratitude,
		}
		messages.append(response_message)
	for tool_call in tool_calls:
		function_name = tool_call.function.name
		function_to_call = available_functions[function_name]
		function_args = json.loads(tool_call.function.arguments)
		function_response = function_to_call (
			post=function_args.get("post"),
		)
		messages.append(
			{
				"tool_call_id": tool_call.id,
				"role": "tool",
				"name": function_name,
				"content": function_response,
			}
		)
	second_response = client.chat.completions.create(
		model="gpt-3.5-turbo-0125",
		messages=messages,
	)
	return second_response
run_conversation()
message = input("give a post\n")
messages.append({"role": "user", "content": f'Find the groups the author of this post is grateful for and why; return it in the format (We thank <community/group/staff/workers> for <reason>) and do it two to three times: {message}'})
print(client.chat.completions.create(model="gpt-3.5-turbo-0125",messages=messages,))