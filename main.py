from PixabayParser import PixabayParser


settings = {
    "Query Settings": {
        "q": "animals",
        "image_type": "photo",
        "per_page": 200
    },
    "Image Limit": 10,
    "Output Directory": "output"
}


parser = PixabayParser(settings)
parser.run()
