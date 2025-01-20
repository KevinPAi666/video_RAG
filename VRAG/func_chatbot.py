from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from openai import OpenAI
import os, json


client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
embeddings = OpenAIEmbeddings()

def brain_reload(videos):
    all_doc = list()
    for i in videos:
        loader = TextLoader(f"{i}.srt")
        documents = loader.load_and_split()
        all_doc = all_doc + documents
        vectorstore = FAISS.from_documents(all_doc, embeddings)
        vectorstore.save_local("embedding")


def query_knowledge_base(embed, query, top_k=2, verbose=1):
    results = embed.similarity_search_with_score(query, top_k=top_k)
    main_reference = (results[0][0].metadata.get('source'), results[0][0].page_content)
    reference = []
    if len(results) > 0:
      for i in results[1:]:
          source_name = i[0].metadata.get('source')
          if source_name not in reference and source_name != main_reference[0]:
              reference.append(source_name)

    return main_reference, reference

def use_prompt_template(main_reference, user_query):
    SYS_PROMPT = """
                  使用者想要知道他的問題在影片中的哪一段出現相關內容，請提出幾個可能有出現的地方並顯示幾分幾秒。
                  格式請參考以下規則：[時間] -> 內容  
                  注意：　
                    1. 不需要幫我回答問題，只需要回答影片中的哪裡有出現與問題相關的內容。
                    2. 參考前後文，若無直接提到問題的關鍵字但可能是相關知識也可以輸出。
                  """
    RAG_INFO = main_reference
    PROMPT = PromptTemplate.from_template("{SYS_PROMPT}{RAG_INFO} \n\n客戶的問題: {QUERY}")
    PROMPT = PROMPT.format(SYS_PROMPT=SYS_PROMPT, RAG_INFO=RAG_INFO, QUERY=user_query)
    return PROMPT

def query_load(user_query):
    video_embed = FAISS.load_local("embedding", embeddings, allow_dangerous_deserialization=True)
    main_reference, reference = query_knowledge_base(video_embed, user_query, verbose=2)
    PROMPT = use_prompt_template(main_reference[1], user_query)
    return PROMPT, main_reference, reference


def openai_ask(question):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": question}],
        max_tokens=4096
    )
    return response.choices[0].message.content

def chat(user_query):
    with open("./file/video_list", 'r', encoding="utf-8") as r:
        videos = json.load(r)

    question, main_reference, reference = query_load(user_query)
    response = openai_ask(question)
    main_reference_source = main_reference[0].split(".srt")[0].split(".mp4")[0]
    reference_source = [i.split(".srt")[0].split(".mp4")[0] for i in reference]
    reference_url = [videos.get(i) for i in reference_source]
    references = []
    for i in range(len(reference_source)):
        references.append(f"{reference_source[i]} - {reference_url[i]}")

    return (f"主題: {main_reference_source}\n"
            f"video URL: {videos.get(main_reference_source)}\n\n"
            f"{response}\n\n\n"
            f"也可以參考:\n" +
            f"\n".join(f"{i + 1}. {ref}" for i, ref in enumerate(references)))

