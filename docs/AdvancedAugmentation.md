[![Memori Labs](https://s3.us-east-1.amazonaws.com/images.memorilabs.ai/banner.png)](https://memorilabs.ai/)

# Introduction to Advanced Augmentation

Memori Advanced Augmentation is an AI/ML driven system for using LLM exchanges to improve context.

## How Does It Work

With Memori, you are creating a schema inside of your datastore by executing the following call:

```python
Memori(conn=db_session_factory).config.storage.build()
```

Advanced Augmentation will automatically insert data into this schema as your users have conversations with an LLM.
