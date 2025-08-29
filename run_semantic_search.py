from elasticsearch import Elasticsearch
from tabulate import tabulate
from colorama import Fore, Back, Style
import os


# Elasticsearch configuration
host = os.getenv('ES_HOST')
api_key = os.getenv('ES_API_KEY')
ES_INDEX = "countries_wiki"  # Index name

# Initialize Elasticsearch client
es = Elasticsearch(
    hosts=host,
    api_key=api_key,
    verify_certs=True,
    request_timeout=600
)

def semantic_search(query, field="wiki_article.sentence", max_results=5):
    """Search using semantic search with chunking"""

    search_body = {
        "_source": ["country"],
        "size": max_results,
        "query": {
            "semantic": {
                "field": field,
                "query": query
            }
        },
        "highlight": {
            "fields": {
                field: {
                    "order": "score",
                    "number_of_fragments": 1
                }
            }
        }
    }

    response = es.search(index="countries_wiki", body=search_body)
    return response
def search_without_chunking(query, max_results=5):
    """Search using semantic search without chunking"""
    return semantic_search(query, field="wiki_article.none", max_results=max_results)

def search_with_chunking(query, max_results=5):
    """Search using semantic search without chunking"""
    return semantic_search(query, field="wiki_article.sentence", max_results=max_results)


def display_results(response, strategy_name, query):
    """Display search results in a nice formatted table"""

    print(f"\n{Fore.LIGHTBLUE_EX}{'=' * 80}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTYELLOW_EX}{Back.BLACK} 🔍 {strategy_name.upper()} SEARCH RESULTS {Style.RESET_ALL}")
    print(f"{Fore.BLUE}Query: '{query}'{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}{'=' * 80}{Style.RESET_ALL}")

    if not response['hits']['hits']:
        print(f"{Fore.RED}❌ No results found{Style.RESET_ALL}")
        return

    # Prepare data for tabulate
    table_data = []

    for i, hit in enumerate(response['hits']['hits'], 1):
        country = hit['_source']['country']
        score = f"{hit['_score']:.3f}"

        # Get highlighted text
        highlights = []
        if 'highlight' in hit:
            for field, fragments in hit['highlight'].items():
                for fragment in fragments:
                    # Clean up fragment and limit length
                    clean_fragment = fragment.replace('<em>', '').replace('</em>', '')
                    if len(clean_fragment) > 500:
                        clean_fragment = clean_fragment[:500] + "..."
                    highlights.append(clean_fragment)

        highlight_text = "\n---\n".join(highlights) if highlights else "No highlights"

        table_data.append([
            f"{Fore.GREEN}{i}{Style.RESET_ALL}",
            f"{Fore.BLUE}{country}{Style.RESET_ALL}",
            f"{Fore.BLUE}{score}{Style.RESET_ALL}",
            f"{Fore.BLACK}{highlight_text}{Style.RESET_ALL}"
        ])

    headers = [
        f"{Fore.RED}Rank{Style.RESET_ALL}",
        f"{Fore.RED}Country{Style.RESET_ALL}",
        f"{Fore.RED}Score{Style.RESET_ALL}",
        f"{Fore.RED}Relevant Chunks{Style.RESET_ALL}"
    ]

    print(tabulate(table_data, headers=headers, tablefmt="grid", maxcolwidths=[None, None, None, 120]))


def compare_search_strategies(query):
    """Compare chunked vs non-chunked search results"""

    print(f"{Fore.GREEN}{Back.BLACK} 🚀 CHUNKING STRATEGY COMPARISON {Style.RESET_ALL}")
    print(f"{Fore.GREEN}Query: '{query}'{Style.RESET_ALL}\n")

    # Search with sentence chunking
    chunked_results = search_with_chunking(query)
    display_results(chunked_results, "WITH CHUNKING (Sentence Strategy)", query)

    # Search without chunking
    non_chunked_results = search_without_chunking(query)
    display_results(non_chunked_results, "WITHOUT CHUNKING", query)

    # Summary comparison
    print(f"\n{Fore.MAGENTA}{'=' * 80}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}{Back.BLACK} 📊 COMPARISON SUMMARY {Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'=' * 80}{Style.RESET_ALL}")

    chunked_count = len(chunked_results['hits']['hits'])
    non_chunked_count = len(non_chunked_results['hits']['hits'])

    comparison_data = [
        ["WITH Chunking", chunked_count,
         f"{chunked_results['hits']['max_score']:.3f}" if chunked_results['hits']['max_score'] else "0"],
        ["WITHOUT Chunking", non_chunked_count,
         f"{non_chunked_results['hits']['max_score']:.3f}" if non_chunked_results['hits']['max_score'] else "0"]
    ]

    comparison_headers = ["Strategy", "Results Found", "Top Score"]
    print(tabulate(comparison_data, headers=comparison_headers, tablefmt="fancy_grid"))


def main():
    """Main function to run the demo"""

    print(f"{Fore.GREEN}{Back.BLACK}🌟 ELASTICSEARCH CHUNKING STRATEGY DEMO 🌟{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'=' * 50}{Style.RESET_ALL}\n")

    # Demo queries
    demo_queries = [
        "countries in the inca empire",
        "coffee production",
        "oil and petroleum exports",
        "beach destinations",
        "hockey"
    ]

    for query in demo_queries:
        compare_search_strategies(query)

    print(f"\n{Fore.GREEN}✨ Demo completed!{Style.RESET_ALL}")


if __name__ == "__main__":
    main()