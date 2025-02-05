'use client';

import {
  ChevronDown,
  ChevronUp,
  Heart,
  MessageCircle,
  Music2,
  Share2,
} from "lucide-react";
import { useEffect, useState } from "react";


// video inference represents the structure of a video object
interface Video {
  video_id: string;
  title: string;
  final_score: number;
}

type ScrollDirection = "up" | "down";
type FeedbackType = "like" | "dislike";

export default function Home() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [currentVideoIndex, setCurrentVideoIndex] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [playedVideoIds, setPlayedVideoIds] = useState<Set<string>>(new Set());
  const [likedVideoIds, setLikedVideoIds] = useState<Set<string>>(new Set());
  const [dislikedVideoIds, setDislikedVideoIds] = useState<Set<string>>(new Set());
  const [playingStates, setPlayingStates] = useState<{ [key: number]: boolean }>({});
  const [currentIndex, setCurrentIndex] = useState<number>(0);

  // Fetch recommendations from the backend
  async function fetchRecommendations(): Promise<void> {
    const playedParam: string = Array.from(playedVideoIds).join(",");
    const likedParam: string = Array.from(likedVideoIds).join(",");
    const dislikedParam: string = Array.from(dislikedVideoIds).join(",");
    try {
      const res = await fetch(
        `http://localhost:5000/recommendations?played=${playedParam}&liked=${likedParam}&disliked=${dislikedParam}`
      );
      const data = await res.json();

      if (Array.isArray(data)) {
        const uniqueVideos: Video[] = Array.from(
          new Map(data.map((video: Video) => [video.video_id, video])).values()
        );
        setVideos(uniqueVideos);
        setCurrentVideoIndex(0);
      } else {
        console.error("Unexpected response from backend:", data);
      }
    } catch (error) {
      console.error("Error fetching recommendations:", error);
    } finally {
      setLoading(false);
      // Initialize playing state for the first video.
      setPlayingStates({ 0: true });
    }
  }

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const handleScroll = (e: React.UIEvent<HTMLDivElement>): void => {
    const container = e.currentTarget;
    const scrollPosition = container.scrollTop;
    const videoHeight = container.clientHeight;
    const index = Math.round(scrollPosition / videoHeight);

    if (index !== currentVideoIndex) {
      setCurrentVideoIndex(index);
      setPlayingStates((prev) => {
        const newStates: { [key: number]: boolean } = { ...prev };
        Object.keys(newStates).forEach((key) => {
          newStates[parseInt(key)] = false;
        });
        newStates[index] = true;
        return newStates;
      });
      setCurrentIndex(index);
    }
  };

  const handleFeedback = (type: FeedbackType, videoIndex: number): void => {
    const video = videos[videoIndex];
    console.log(`Video ${video.video_id} received ${type}`);

    setPlayedVideoIds((prev) => new Set(prev).add(video.video_id));

    if (type === "like") {
      setLikedVideoIds((prev) => new Set(prev).add(video.video_id));
    } else {
      setDislikedVideoIds((prev) => new Set(prev).add(video.video_id));
    }

    if (videoIndex === videos.length - 1) {
      setLoading(true);
      fetchRecommendations();
    }
  };

  const togglePlay = (index: number): void => {
    setPlayingStates((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };


  // scroll video function
  const scrollToVideo = (direction: ScrollDirection): void => {
    const container = document.querySelector(".video-container") as HTMLElement;
    const videoHeight: number = container.clientHeight;
    const nextIndex: number =
      direction === "up" ? currentVideoIndex - 1 : currentVideoIndex + 1;
  
    // When scrolling down, mark the current video as played.
    if (direction === "down") {
      const currentVideo = videos[currentVideoIndex];
      setPlayedVideoIds((prev) => new Set(prev).add(currentVideo.video_id));
    }
  
    if (nextIndex >= 0 && nextIndex < videos.length) {
      container.scrollTo({
        top: nextIndex * videoHeight,
        behavior: "smooth",
      });
      setCurrentVideoIndex(nextIndex);
      setCurrentIndex(nextIndex);
    } else if (nextIndex >= videos.length) {
      // At the end of the list, fetch new recommendations.
      setLoading(true);
      fetchRecommendations();
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-black">
        <p className="text-white text-xl">Loading Recommendations...</p>
      </div>
    );
  }

  if (videos.length === 0) {
    return (
      <div className="flex items-center justify-center h-screen bg-black">
        <p className="text-white text-xl">No videos available</p>
      </div>
    );
  }

  return (
    <div
      className="video-container h-screen overflow-y-scroll snap-y snap-mandatory relative"
      onScroll={handleScroll}
    >
      {videos.map((video, index) => (
        <div
          key={video.video_id}
          className="relative w-full h-screen bg-black overflow-hidden snap-start"
        >
          {/* Video container with click handler */}
          <div className="absolute inset-0" onClick={() => togglePlay(index)}>
            {playingStates[index] ? (
              <iframe
                src={`https://www.youtube.com/embed/${video.video_id}?autoplay=1&controls=0&modestbranding=1`}
                title={video.title}
                frameBorder="0"
                allow="autoplay; encrypted-media"
                allowFullScreen
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="relative w-full h-full">
                <img
                  src={`https://img.youtube.com/vi/${video.video_id}/hqdefault.jpg`}
                  alt={video.title}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 flex items-center justify-center">
                  <svg
                    className="w-16 h-16 text-white opacity-80"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M8 5v14l11-7z" />
                  </svg>
                </div>
              </div>
            )}
          </div>

          {/* Navigation Arrows */}
          <div className="absolute left-1/2 transform -translate-x-1/2 z-20 flex flex-col items-center gap-4 bottom-4">
            {currentIndex > 0 && (
              <button
                onClick={() => scrollToVideo("up")}
                className="w-12 h-12 flex items-center justify-center rounded-full bg-gray-800/50 hover:bg-gray-700/50 transition-colors"
              >
                <ChevronUp className="w-8 h-8 text-white" />
              </button>
            )}
            <button
              onClick={() => scrollToVideo("down")}
              className="w-12 h-12 flex items-center justify-center rounded-full bg-gray-800/50 hover:bg-gray-700/50 transition-colors"
            >
              <ChevronDown className="w-8 h-8 text-white" />
            </button>
          </div>

          {/* Vertical action bar - right side */}
          <div className="absolute right-4 bottom-20 flex flex-col items-center gap-6 z-10">
            <div className="w-12 h-12 rounded-full bg-gray-300 overflow-hidden mb-4">
              <img
                src="/api/placeholder/40/40"
                alt="Profile"
                className="w-full h-full object-cover"
              />
            </div>

            <button
              onClick={() => handleFeedback("like", index)}
              className="flex flex-col items-center gap-1"
            >
              <div className="w-12 h-12 flex items-center justify-center rounded-full bg-gray-800/50">
                <Heart
                  className={`w-7 h-7 ${
                    likedVideoIds.has(video.video_id) ? "text-red-500" : "text-white"
                  }`}
                  fill={likedVideoIds.has(video.video_id) ? "currentColor" : "none"}
                />
              </div>
              <span className="text-white text-xs">
                {Math.floor(video.final_score * 1000)}
              </span>
            </button>

            <button className="flex flex-col items-center gap-1">
              <div className="w-12 h-12 flex items-center justify-center rounded-full bg-gray-800/50">
                <MessageCircle className="w-7 h-7 text-white" />
              </div>
              <span className="text-white text-xs">Comments</span>
            </button>

            <button className="flex flex-col items-center gap-1">
              <div className="w-12 h-12 flex items-center justify-center rounded-full bg-gray-800/50">
                <Share2 className="w-7 h-7 text-white" />
              </div>
              <span className="text-white text-xs">Share</span>
            </button>
          </div>

          {/* Video info - bottom */}
          <div className="absolute bottom-0 left-0 p-4 w-full z-10">
            <div className="max-w-[80%]">
              <h2 className="text-white font-semibold mb-2">{video.title}</h2>
              <div className="flex items-center gap-2">
                <Music2 className="w-4 h-4 text-white" />
                <p className="text-white text-sm">Original Sound</p>
              </div>
            </div>
          </div>

          {/* Gradient overlay */}
          <div className="absolute bottom-0 left-0 w-full h-48 bg-gradient-to-t from-black/60 to-transparent" />
        </div>
      ))}
    </div>
  );
}