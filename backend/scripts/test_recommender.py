from backend.src.recommender import AdaptiveRecommender

def test():
    rec = AdaptiveRecommender()
    try:
        r = rec.recommend(1)
        print("Success:", r)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
