from src.preprocessing.image_cleaner import simple_resize_if_large
from pathlib import Path
def test_resize(tmp_path):
    p = tmp_path / "test.png"
    # create small sample image
    from PIL import Image
    Image.new('RGB', (100,100), color='white').save(p)
    out = tmp_path / "out.png"
    simple_resize_if_large(str(p), str(out), max_side=50)
    assert Path(out).exists()
