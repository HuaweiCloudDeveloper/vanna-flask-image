## 目标

基于 [vanna-flask](https://github.com/vanna-ai/vanna-flask) ，搭建基于OpenAI +Milvus+MySQL的解决方案示例，帮助开发者方便移植到企业应用中。本示例LLM支持OpenAI接口的模型服务，Milvus+MySQL支持远程连接，同时支持本地搭建。

## 构建步骤

**1.下载vanna-flask**

```shell
git clone https://github.com/vanna-ai/vanna-flask.git
cd vanna-flask
```

**2.修改`requirements.txt`**

```shell
flask
vanna[milvus,openai,mysql]
db-dtypes
python-dotenv
cryptography
```

3.创建`core.py`

```shell
from vanna.openai.openai_chat import OpenAI_Chat
from vanna.milvus.milvus_vector import Milvus_VectorStore
from openai import OpenAI
from pymilvus import MilvusClient
from pymilvus.model.dense.openai import OpenAIEmbeddingFunction

class Extra_OpenAI_Chat(OpenAI_Chat):

    def __init__(self,config={}):
        super().__init__(config)

    def submit_prompt(self, prompt, **kwargs) -> str:
        if prompt is None:
            raise Exception("Prompt is None")

        if len(prompt) == 0:
            raise Exception("Prompt is empty")

        response = self.client.chat.completions.create(
                model=self.config.get("OPENAI_LLM_MODEL"),
                messages=prompt,
                stop=None,
                temperature=self.temperature,
                extra_body={
                    "chat_template_kwargs": {
                        "enable_thinking": False
                    }
                }
            )

        for choice in response.choices:
            if "text" in choice:
                return choice.text

        return response.choices[0].message.content
    
class VannaService(Extra_OpenAI_Chat,Milvus_VectorStore):

    def __init__(self,config={}):
        
        config["milvus_client"] = MilvusClient(
                uri = config.get("MILVUS_URI"),
                user = config.get("MILVUS_USER"),
                password = config.get("MILVUS_PASSWORD"))
            
        config["embedding_function"] = OpenAIEmbeddingFunction(
                model_name = config.get("OPENAI_EMBEDDING_MODEL"),
                api_key = config.get("OPENAI_EMBEDDING_API_KEY"),
                base_url = config.get("OPENAI_EMBEDDING_BASE_URL"),
            )
            
        # 配置milvus
        Milvus_VectorStore.__init__(self, config)
        # 配置openai
        OpenAI_Chat.__init__(self,
            client=OpenAI(
                api_key = config.get("OPENAI_LLM_API_KEY"),
                base_url = config.get("OPENAI_LLM_BASE_URL")),
            config=config)
        # 配置mysql连接
        super().connect_to_mysql(
            host = config.get("MYSQL_HOST"),
            dbname = config.get("MYSQL_DBNAME"),
            user = config.get("MYSQL_USER"),
            password = config.get("MYSQL_PASSWORD"),
            port = int(config.get("MYSQL_PORT")))

```

**3.修改`app.py`**

```shell
# 需替换的代码
from vanna.remote import VannaDefault
vn = VannaDefault(model=os.environ['VANNA_MODEL'], api_key=os.environ['VANNA_API_KEY'])

vn.connect_to_snowflake(
    account=os.environ['SNOWFLAKE_ACCOUNT'],
    username=os.environ['SNOWFLAKE_USERNAME'],
    password=os.environ['SNOWFLAKE_PASSWORD'],
    database=os.environ['SNOWFLAKE_DATABASE'],
    warehouse=os.environ['SNOWFLAKE_WAREHOUSE'],
)

app.run(debug=True)

# 替换的代码
from core import VannaService
config = {
    "OPENAI_LLM_API_KEY": os.getenv("OPENAI_LLM_API_KEY"),
    "OPENAI_LLM_BASE_URL": os.getenv("OPENAI_LLM_BASE_URL"),
    "OPENAI_LLM_MODEL": os.getenv("OPENAI_LLM_MODEL"),
    "OPENAI_EMBEDDING_API_KEY": os.getenv("OPENAI_EMBEDDING_API_KEY"),
    "OPENAI_EMBEDDING_BASE_URL": os.getenv("OPENAI_EMBEDDING_BASE_URL"),
    "OPENAI_EMBEDDING_MODEL": os.getenv("OPENAI_EMBEDDING_MODEL"),
    "MILVUS_URI": os.getenv("MILVUS_URI"),
    "MILVUS_USER": os.getenv("MILVUS_USER"),
    "MILVUS_PASSWORD": os.getenv("MILVUS_PASSWORD"),
    "MYSQL_HOST": os.getenv("MYSQL_HOST"),
    "MYSQL_PORT": os.getenv("MYSQL_PORT"),
    "MYSQL_DBNAME": os.getenv("MYSQL_DBNAME"),
    "MYSQL_USER": os.getenv("MYSQL_USER"),
    "MYSQL_PASSWORD": os.getenv("MYSQL_PASSWORD"),
}
vn = VannaService(config)

app.run(host='0.0.0.0', port=8080)
```
