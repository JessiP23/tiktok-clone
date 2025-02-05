'use client';

import { useEffect, useState } from "react";
import Image from "next/image";

interface Video {
  video_id: string;
  title: string;
  final_score: number;
}

export default function Home() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [currentVideoIndex, setCurrentVideoIndex] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  // Track played video IDs to exclude them from future recommendations.
  const [playedVideoIds, setPlayedVideoIds] = useState<Set<string>>(new Set());

  // Fetch recommendations from the backend.
  async function fetchRecommendations() {
    // Build query parameter: played IDs as comma separated string.
    const playedParam = Array.from(playedVideoIds).join(",");
    const res = await fetch(`http://localhost:5000/recommendations?played=${playedParam}`);
    const data: Video[] = await res.json();
    // Filter duplicates, just in case.
    const uniqueVideos = Array.from(
      new Map(data.map((video) => [video.video_id, video])).values()
    );
    setVideos(uniqueVideos);
    setCurrentVideoIndex(0);
    setLoading(false);
  }
  
  // Initial fetch.
  useEffect(() => {
    fetchRecommendations();
  }, []);

  // Process feedback and advance to next video.
  const handleFeedback = (type: "like" | "dislike") => {
    const currentVideo = videos[currentVideoIndex];
    // Add current video id to played list.
    setPlayedVideoIds((prev) => new Set(prev).add(currentVideo.video_id));

    // Example: Later send this feedback to the backend for personalized training.
    // For now, simply log it:
    console.log(`Video ${currentVideo.video_id} received ${type}`);

    // If this was the last video in the current recommendations, fetch new ones.
    if (currentVideoIndex === videos.length - 1) {
      setLoading(true);
      fetchRecommendations();
    } else {
      setCurrentVideoIndex((prev) => prev + 1);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-black">
        <p className="text-white text-xl">Loading Recommendations...</p>
      </div>
    );
  }

  // If no recommendations at all.
  if (videos.length === 0) {
    return (
      <div className="flex items-center justify-center h-screen bg-black">
        <p className="text-white text-xl">No videos available</p>
      </div>
    );
  }

  const video = videos[currentVideoIndex];

  return (
    <div className="relative w-full h-screen bg-black overflow-hidden">
      {/* YouTube embed to play current video automatically */}
      <div className="absolute inset-0">
        <iframe
          src={`https://www.youtube.com/embed/${video.video_id}?autoplay=1&controls=0&modestbranding=1`}
          title={video.title}
          frameBorder="0"
          allow="autoplay; encrypted-media"
          allowFullScreen
          className="w-full h-full"
        />
        <div className="absolute inset-0 bg-black opacity-30" />
      </div>
      {/* Video details overlay (bottom left) */}
      <div className="absolute bottom-10 left-6 text-white z-10">
        <h2 className="text-2xl font-bold mb-2">{video.title}</h2>
        <p className="text-sm">Score: {video.final_score.toFixed(3)}</p>
      </div>
      {/* Like/Dislike buttons overlay (right side) */}
      <div className="absolute right-6 bottom-20 flex flex-col gap-4 z-10">
        <button
          onClick={() => handleFeedback("like")}
          className="w-14 h-14 flex items-center justify-center rounded-full bg-green-600 shadow-lg"
        >
          <svg
            className="w-7 h-7 text-white"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M3 10a1 1 0 011-1h4V5a1 1 0 112 0v4h4a1 1 0 110 2h-4v4a1 1 0 11-2 0v-4H4a1 1 0 01-1-1z" />
          </svg>
        </button>
        <button
          onClick={() => handleFeedback("dislike")}
          className="w-14 h-14 flex items-center justify-center rounded-full bg-red-600 shadow-lg"
        >
          <svg
            className="w-7 h-7 text-white"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M17 10a1 1 0 00-1-1h-4V5a1 1 0 00-2 0v4H4a1 1 0 000 2h6v4a1 1 0 002 0v-4h4a1 1 0 001-1z" />
          </svg>
        </button>
      </div>
    </div>
  );
}