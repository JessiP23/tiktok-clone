export interface Video {
    id: number,
    title: string,
}

export interface Rating {
    userId: number,
    videoId: number,
    // 1-5
    rating: number,
}

export const videos: Video[] = [
    {id: 1, title: 'Introduction to React'},
    { id: 2, title: 'Advanced TypeScript' },
    { id: 3, title: 'Next.js tutorial' },
    { id: 4, title: 'Machine Learning basics' },
    { id: 5, title: 'Myvideo' }
];

export const ratings: Rating[] = [
    {userId: 1, videoId: 1, rating: 5},
    {userId: 1, videoId: 2, rating: 4},
    {userId: 2, videoId: 3, rating: 3},
    {userId: 3, videoId: 4, rating: 2},
    {userId: 2, videoId: 5, rating: 1},
    {userId: 2, videoId: 1, rating: 2},
]