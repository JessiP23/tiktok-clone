export interface Video {
    id: string;
    title: string;
    url: string;
    likes: number;
}

export interface User {
    id: string;
    name: string;
    // array of liked videos
    likedVideos: string[];
}

export interface Rating {
    userId: string;
    videoId: string;

    // liked videos - 1 , disliked videos - 0
    score: number;
}