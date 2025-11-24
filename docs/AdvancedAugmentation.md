[![Memori Labs](https://s3.us-east-1.amazonaws.com/images.memorilabs.ai/banner.png)](https://memorilabs.ai/)

# Introduction to Advanced Augmentation

Memori Advanced Augmentation is an AI/ML driven system for using LLM exchanges to improve context.

## How Does It Work

With Memori, you are creating a schema inside of your datastore by executing the following call:

```python
Memori(conn=db_session_factory).config.storage.build()
```

Advanced Augmentation will automatically insert data into this schema as a user (for example) has conversations with an LLM.

Memori is able to process these conversations once you register your LLM client. Here is an example registering an OpenAI client:

```python
from openai import OpenAI
from memori import Memori

client = OpenAI(...)
mem = Memori().openai.register(client)
```

## Conversations

The back and forth questions and statements and responses from the LLM are automatically stored inside your database. Memori will recall and add the messages to subsequent LLM calls. We call this conversation tracking.

Tables involved in Conversations:
- memori_conversation
- memori_conversation_message

## Sessions

The back and forth exchanges with the LLM are automatically grouped together into a session. This ensures you can recall entire conversations that were related to a particular conversation between the user and the LLM.

Table involved in Sessions:
- memori_session
