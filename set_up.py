import wikipedia
from elasticsearch import Elasticsearch
from colorama import Fore, Back, Style
import time
import os


# Elasticsearch configuration
host = os.getenv('ES_HOST')
api_key = os.getenv('ES_API_KEY')
ES_INDEX = "countries_wiki"  # Index name

# List of countries in the Americas
countries = [
    "United States", "Canada", "Mexico", "Guatemala", "Belize", "Honduras",
    "El Salvador", "Nicaragua", "Costa Rica", "Panama", "Cuba", "Jamaica",
    "Haiti", "Dominican Republic", "Trinidad and Tobago", "Barbados",
    "Brazil", "Argentina", "Chile", "Peru", "Colombia", "Venezuela",
    "Ecuador", "Bolivia", "Paraguay", "Uruguay"
]


# Initialize Elasticsearch client
es = Elasticsearch(
    hosts=host,
    api_key=api_key,
    verify_certs=True,
    request_timeout=600
)


def setup_inference_models():
    """Set up the inference models for chunking strategies"""

    print(f"{Fore.CYAN}🔧 Setting up inference models...{Style.RESET_ALL}")

    # Create sentence embedding model with chunking
    sentence_chunking = {
        "task_type": "sparse_embedding",
        "service": "elasticsearch",
        "service_settings": {
            "num_allocations": 1,
            "num_threads": 2,
            "model_id": ".elser_model_2_linux-x86_64"
        },
        "chunking_settings": {
            "strategy": "sentence",
            "max_chunk_size": 80,
            "sentence_overlap": 1
        }
    }

# Create sentence embedding model with chunking
    none_chunking = {
        "task_type": "sparse_embedding",
        "service": "elasticsearch",
        "service_settings": {
            "num_allocations": 1,
            "num_threads": 2,
            "model_id": ".elser_model_2_linux-x86_64"
        },
        "chunking_settings": {
            "strategy": "none"
        }
    }

    # Define strategies with their names and inference IDs
    chunking_strategies = [
        {
            "config": sentence_chunking,
            "inference_id": "sentence-chunking-demo",
            "name": "Sentence Chunking Strategy"
        },
        {
            "config": none_chunking,
            "inference_id": "none-chunking-demo",
            "name": "No Chunking Strategy"
        }
    ]

    for strategy in chunking_strategies:
        try:
            es.inference.put(
                inference_id=strategy["inference_id"],
                body=strategy["config"]
            )
            print(f"{Fore.GREEN}✓ {strategy["inference_id"]}embedding model created{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ Non-chunked model might already exist: {e}{Style.RESET_ALL}")


def setup_index():
    """Set up the countries_wiki index with proper mappings"""

    print(f"\n{Fore.CYAN}🗂️  Setting up index...{Style.RESET_ALL}")

    # Delete existing index
    try:
        es.indices.delete(index="countries_wiki")
        print(f"{Fore.YELLOW}🗑️  Deleted existing index{Style.RESET_ALL}")
    except:
        pass

    # Create new index with mappings
    mapping = {
        "mappings": {
            "properties": {
                "country": {
                    "type": "keyword"
                },
                "wiki_article": {
                    "type": "text",
                    "fields": {
                        "none": {
                            "type": "semantic_text",
                            "inference_id": "none-chunking-demo"
                        },
                        "sentence": {
                            "type": "semantic_text",
                            "inference_id": "sentence-chunking-demo"
                        }
                    }
                }
            }
        }
    }

    es.indices.create(index="countries_wiki", body=mapping)
    print(f"{Fore.GREEN}✓ Index created with semantic text mappings{Style.RESET_ALL}")

def upload_documents(countries):
    # List to store all country data
    countries_data = []

    for country in countries:
            try:
                # Get Wikipedia content
                content = wikipedia.page(title=country, auto_suggest=False).content

                # Create JSON object
                country_json = {
                    "country": country,
                    "wiki_article": content
                }

                # Append to list
                countries_data.append(country_json)

                # Upload to Elasticsearch
                es_response = es.index(
                    index=ES_INDEX,
                    body=country_json, timeout='600s'
                )


                print(f"✓ {country}: Uploaded to ES with ID {es_response['_id']}")



            except Exception as e:
                print(f"Error with {country}: {e}")

    print(f"Total countries collected: {len(countries_data)}")


def main():
    """Main function to run the demo"""
    start_time = time.time()
    print(f"{Fore.GREEN}{Back.BLACK}🌟 ELASTICSEARCH CHUNKING STRATEGY DEMO 🌟{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'=' * 50}{Style.RESET_ALL}\n")

    # Setup
    setup_inference_models()
    setup_index()
    upload_documents(countries)

    print(f"\n{Fore.YELLOW}⏳ Waiting for index to be ready... ")


    print(f"\n{Fore.GREEN}✨ Set up completed!{Style.RESET_ALL}")

    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == "__main__":
    main()