
import instaloader
import os
import re
import shutil
from glob import glob

class InstagramDownloader:
    def __init__(self, download_path="downloads"):
        self.download_base_path = download_path
        # Ensure base download directory exists
        os.makedirs(self.download_base_path, exist_ok=True)
        
        self.L = instaloader.Instaloader(
            dirname_pattern=str(self.download_base_path) + "/{target}",
            download_pictures=True,
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )

    def get_shortcode_from_url(self, url):
        match = re.search(r'instagram\.com/(?:p|reel|tv|stories/[^/]+)/([^/?#&]+)', url)
        if match:
            return match.group(1)
            
        # Fallback for simple share URLs if needed, but standard ones usually match
        return None

    def download_post(self, url):
        shortcode = self.get_shortcode_from_url(url)
        if not shortcode:
            raise ValueError("Could not exact shortcode from URL")

        target_dir = os.path.join(self.download_base_path, shortcode)
        
        # Clean existing if any (unlikely with unique timestamps but shortcode is unique per post)
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)

        try:
            post = instaloader.Post.from_shortcode(self.L.context, shortcode)
            
            # Verify if it's the right content
            self.L.download_post(post, target=shortcode)
            
            # Gather files
            # Instaloader saves with various extensions. We want .jpg, .mp4
            files = []
            
            # Collect all media files
            # We sort them to maintain order for carousels (usually numbered)
            media_files = sorted(glob(os.path.join(target_dir, "*")))
            
            valid_extensions = {'.jpg', '.jpeg', '.png', '.mp4'}
            final_files = [f for f in media_files if os.path.splitext(f)[1].lower() in valid_extensions]
            
            if not final_files:
                raise Exception("No media files found after download.")
                
            return final_files, post.typename, target_dir

        except Exception as e:
            # Cleanup on failure if created
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            raise e

    def cleanup(self, path):
        if os.path.exists(path):
            shutil.rmtree(path)
