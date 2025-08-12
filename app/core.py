
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

    def __init__(self,config):
        print("配置项:",config)
        config["milvus_client"] = MilvusClient(
                uri = config["MILVUS_URI"],
                user = config["MILVUS_USER"],
                password = config["MILVUS_PASSWORD"]
            )
        print("milvus_client实例化成功...")    
        config["embedding_function"] = OpenAIEmbeddingFunction(
                model_name = config["OPENAI_EMBEDDING_MODEL"],
                api_key = config["OPENAI_EMBEDDING_API_KEY"],
                base_url = config["OPENAI_EMBEDDING_BASE_URL"]
            )
        print("embedding_function实例化成功...")
        # 配置milvus
        Milvus_VectorStore.__init__(self, config)
        print("milvus实例化成功...")
        # 配置openai
        OpenAI_Chat.__init__(self,
            client=OpenAI(
                api_key = config["OPENAI_LLM_API_KEY"],
                base_url = config["OPENAI_LLM_BASE_URL"]),
            config=config)
        print("OpenAI_Chat实例化成功...")
        # 配置mysql连接
        super().connect_to_mysql(
            host = config["MYSQL_HOST"],
            dbname = config["MYSQL_DBNAME"],
            user = config["MYSQL_USER"],
            password = config["MYSQL_PASSWORD"],
            port = int(config["MYSQL_PORT"]))
        print("mysql连接成功...")
