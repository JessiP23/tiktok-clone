import { useEffect, useState } from "react";
import Image from "next/image";

interface Video {
  video_id: string;
  title: string;
  final_score: number;
}

export default function Home() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function fetchRecommendations() {
      // Adjust URL if needed (e.g., your Flask backend host and port)
      const res = await fetch("http://localhost:5000/recommendations");
      const data = await res.json();
      setVideos(data);
      setLoading(false);
    }
    fetchRecommendations();
  }, []);

  return (
    <div className="min-h-screen p-8 pb-20 gap-16 sm:p-20 flex flex-col items-center">
      <h1 className="text-2xl font-bold mb-8">Recommended Videos</h1>
      {loading ? (
        <p>Loading recommendations...</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8">
          {videos.map((video) => (
            <div key={video.video_id} className="border rounded p-4">
              {/* Use YouTube thumbnail URL */}
              <Image
                src={`https://img.youtube.com/vi/${video.video_id}/hqdefault.jpg`}
                alt={video.title}
                width={320}
                height={180}
              />
              <h2 className="mt-4 font-semibold">{video.title}</h2>
              <p className="text-sm">
                Score: {video.final_score.toFixed(3)}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}