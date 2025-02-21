# Web Scraping Assignment - Ken Lai

### Approach
The initial step in developing the scraping solution involved thorough research and analysis of the target website, focusing particularly on how content is dynamically loaded. The scraping script was developed using Scrapy, a robust scraping framework in Python, combined with Playwright, an advanced automation library that excels in interacting with dynamic web pages. This combination provides a powerful solution for tackling common challenges faced in web scraping projects: including:
- **Dynamic Content Loading**:
Playwright is utilized to handle JavaScript-heavy elements and AJAX-loaded content, ensuring complete page data is captured.
- **Error Handling**: 
The script is designed to handle exceptions gracefully; if an error occurs during data extraction or a bad response is received, it logs the error and continues processing other requests without interruption.
- **Retry Mechanism**:
    Scrapy will automatically retry the scrapping 2 times by default
- **Data Integrity**: 
The script includes validations to ensure the accuracy and format of scraped data, with default values provided for missing fields as shown in the table below.

| Field | Default Value  |
| ------- | --- |
| product_name | null |
| product_images | [] |
| quantity | null |
| product_name | null |
| barcode_number | null |
| product_details | null |
| price | null |
| labels | [] |

### Dependencies

- Python 3.13: For running the script.
- Scrapy: For asynchronous data scraping.
- Playwright: To interact with JavaScript-heavy pages for dynamic contents.

Please refer to requirement.txt for more details.

## How to run

### In the project folder
`

    # Mac
    # create Python virtual environment
    python -m venv .venv
    
    # activate the virtual environment
    source .venv/bin/activate
    
    # install dependencies
    pip install -r requirements.txt
    
    # append to the existing  data.csv file, if it exists
    scrapy crawl tops_online -o data.csv
    # overwrite to the existing one, if it exists
    scrapy crawl tops_online -O data.csv
`

## Challenges and Solutions
### Dynamically Loaded Contents:
The website features content that loads dynamically as the user interacts with the page, such as scrolling or clicking buttons. Traditional scraping tools struggle with this as they do not execute JavaScript. To handle this, I integrated Playwright with Scrapy, which allows the execution of JavaScript, ensuring that all dynamically loaded contents are rendered and accessible for scraping. Playwright's capability to wait for elements to appear and interact with AJAX calls ensures that all relevant data is loaded before scraping.

### Slow Loading Pages: 
Some pages on the website load slowly, which can interrupt the scraping process. This was mitigated by implementing a longer timeout in Playwright to ensure the page loads completely before data extraction begins.

### Infinite Scrolling: 
The product lists on the website use an infinite scrolling mechanism that dynamically loads content as the user scrolls. To handle this, Playwright scripts were used to automatically scroll to the bottom of the page until all products are loaded before scraping begins.

### Anti-bot
Although this project did not suffer from anti-bot challenges, it is crucial to be prepared for such issues. If the site were to implement anti-bot measures, potential strategies to overcome them would include:
- **Rotating Proxies**: Using a pool of proxies to frequently change the IP address during sessions to prevent detection and blocking.
- **User-Agent Rotation**: Implementing a mechanism to rotate user agents with each request to mimic different devices and browsers, reducing the likelihood of being flagged as a bot.


## Sample Output

```json
[
{
    "product_name": "Ushibori Pure Apple Vinegar",
    "product_images": [
        "https://assets.tops.co.th/UCHIBORI-UshiboriPureAppleVinegar500ml-4970285850132-1?$JPEG$",
        "https://assets.tops.co.th/UCHIBORI-UshiboriPureAppleVinegar500ml-4970285850132-1?$JPEG$",
        "https://assets.tops.co.th/UCHIBORI-UshiboriPureAppleVinegar500ml-4970285850132-2?$JPEG$",
        "https://assets.tops.co.th/UCHIBORI-UshiboriPureAppleVinegar500ml-4970285850132-3?$JPEG$"
    ],
    "bar_code_number": "4970285850132",
    "product_details": "Properties\n                            :\n                            \n                                The product received may be subject to package modification and quantity from the manufacturer.\nWe reserve the right to make any changes without prior notice. \n*The images used are for advertising purposes only.",
    "price": 270.0,
    "labels": [
        "Sale",
        "Today - 4 Mar 2025"
    ],
    "url": "https://www.tops.co.th/en/ushibori-pure-apple-vinegar-500ml-4970285850132",
    "category": "Pantry & Ingredients",
    "subcategory": "Seasonings & Spices",
    "quantity": "500ml"
},
{
    "product_name": "Chao Thai Coconut Powder",
    "product_images": [
        "https://assets.tops.co.th/CHAOTHAI-ChaoThaiCoconutPowder60g-8852114531602-1",
        "https://assets.tops.co.th/CHAOTHAI-ChaoThaiCoconutPowder60g-8852114531602-1",
        "https://assets.tops.co.th/CHAOTHAI-ChaoThaiCoconutPowder60g-8852114531602-2"
    ],
    "bar_code_number": "8852114531602",
    "product_details": "Properties\n                            :\n                            \n                                The product received may be subject to package modification and quantity from the manufacturer.\nWe reserve the right to make any changes without prior notice. \n*The images used are for advertising purposes only.",
    "price": 18.0,
    "labels": [],
    "url": "https://www.tops.co.th/en/chao-thai-coconut-powder-60g-8852114531602",
    "category": "Pantry & Ingredients",
    "subcategory": "Seasonings & Spices",
    "quantity": "60g"
},
{
    "product_name": "Zab Mike Pasteurized Thai Fermented Fish Sauce",
    "product_images": [
        "https://assets.tops.co.th/ZABMIKE-ZabMikePasteurizedThaiFermentedFishSauce330ml-8858981500901-1?$JPEG$",
        "https://assets.tops.co.th/ZABMIKE-ZabMikePasteurizedThaiFermentedFishSauce330ml-8858981500901-1?$JPEG$",
        "https://assets.tops.co.th/ZABMIKE-ZabMikePasteurizedThaiFermentedFishSauce330ml-8858981500901-2?$JPEG$",
        "https://assets.tops.co.th/ZABMIKE-ZabMikePasteurizedThaiFermentedFishSauce330ml-8858981500901-3?$JPEG$"
    ],
    "bar_code_number": "8858981500901",
    "product_details": "Properties\n                            :\n                            \n                                The product received may be subject to package modification and quantity from the manufacturer.\nWe reserve the right to make any changes without prior notice. \n*The images used are for advertising purposes only.",
    "price": 40.0,
    "labels": [],
    "url": "https://www.tops.co.th/en/zab-mike-pasteurized-thai-fermented-fish-sauce-330ml-8858981500901",
    "category": "Pantry & Ingredients",
    "subcategory": "Seasonings & Spices",
    "quantity": "330ml"
},
{
    "product_name": "Mccormick Original Taco",
    "product_images": [
        "https://assets.tops.co.th/MCCORMICK-MccormickOriginalTaco28g-0052100091709-1?$JPEG$",
        "https://assets.tops.co.th/MCCORMICK-MccormickOriginalTaco28g-0052100091709-1?$JPEG$",
        "https://assets.tops.co.th/MCCORMICK-MccormickOriginalTaco28g-0052100091709-2?$JPEG$"
    ],
    "bar_code_number": "0052100091709",
    "product_details": "Properties\n                            :\n                            \n                                Mccormick Original Taco Standard qualityMade from high quality raw materialsMade from good quality factory\n\nThe product received may be subject to package modification and quantity from the manufacturer.\nWe reserve the right to make any changes without prior notice. \n*The images used are for advertising purposes only.",
    "price": 50.0,
    "labels": [],
    "url": "https://www.tops.co.th/en/mccormick-original-taco-28g-0052100091709",
    "category": "Pantry & Ingredients",
    "subcategory": "Seasonings & Spices",
    "quantity": "28g"
},
{
    "product_name": "Mae Houy Flaked Dried Radish",
    "product_images": [
        "https://assets.tops.co.th/MAEHOUY-MaeHouyFlakedDriedRadish200g-8853853000022-1",
        "https://assets.tops.co.th/MAEHOUY-MaeHouyFlakedDriedRadish200g-8853853000022-1"
    ],
    "bar_code_number": "8853853000022",
    "product_details": "Properties\n                            :\n                            \n                                The product received may be subject to package modification and quantity from the manufacturer.\nWe reserve the right to make any changes without prior notice. \n*The images used are for advertising purposes only.",
    "price": 59.0,
    "labels": [],
    "url": "https://www.tops.co.th/en/mae-houy-flaked-dried-radish-200g-8853853000022",
    "category": "Pantry & Ingredients",
    "subcategory": "Seasonings & Spices",
    "quantity": "200g"
},
{
    "product_name": "Mccormick Sea Salt Grinder",
    "product_images": [
        "https://assets.tops.co.th/MCCORMICK-MccormickSeaSaltGrinder60g-0052100746029-1",
        "https://assets.tops.co.th/MCCORMICK-MccormickSeaSaltGrinder60g-0052100746029-1"
    ],
    "bar_code_number": "0052100746029",
    "product_details": "Properties\n                            :\n                            \n                                Mccormick Sea Salt Grinder Standard qualityMade from high quality raw materialsMade from good quality factory\n\nThe product received may be subject to package modification and quantity from the manufacturer.\nWe reserve the right to make any changes without prior notice. \n*The images used are for advertising purposes only.",
    "price": 127.0,
    "labels": [],
    "url": "https://www.tops.co.th/en/mccormick-sea-salt-grinder-60g-0052100746029",
    "category": "Pantry & Ingredients",
    "subcategory": "Seasonings & Spices",
    "quantity": "60g"
},
]
```