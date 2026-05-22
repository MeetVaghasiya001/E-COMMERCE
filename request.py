import requests

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}

query = f"""
            query productDetails($variantsCursor: String) @inContext(country: IN, language: EN) {{
            product(handle: "preview-bk") {{
                id
                handle
                title
                vendor
                availableForSale
                onlineStoreUrl
                tags
                publishedAt

                priceRange {{
                    maxVariantPrice {{ amount }}
                    minVariantPrice {{ amount }}
                }}

                featuredImage {{ id url }}

                options {{
                    id
                    name
                    values
                    optionValues {{ id name }}
                }}

                images(first: 250) {{
                    nodes {{ id url altText }}
                }}

                variants(first: 250, after: $variantsCursor) {{
                    nodes {{
                        id
                        availableForSale

                        compareAtPrice {{
                            currencyCode
                            amount
                        }}

                        selectedOptions {{
                            name
                            value
                        }}

                        currentlyNotInStock

                        featured_image: image {{
                            id
                            src: url
                            altText
                        }}

                        price {{
                            currencyCode
                            amount
                        }}

                        title
                        sku
                    }}

                    pageInfo {{
                        hasNextPage
                        endCursor
                    }}
                }}

                compareAtPriceRange {{
                    maxVariantPrice {{ amount }}
                    minVariantPrice {{ amount }}
                }}
            }}
            }}
        """

json_data = {
    "query": query,
    "variables": {}
}

data = requests.post('https://thebearhouse.com/api/2025-10/graphql.json',json = json_data)
print(data.text)