import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { fetchVideo } from '../api/content';
import { ApiError } from '../api/client';
import type { VideoDetail } from '../types';
import { EmptyState, ErrorState, LoadingState, PageHeader } from '../components/ui';
import { VideoIcon } from '../components/icons';
import { VideoPlayer } from '../components/VideoPlayer';

type LoadState = 'loading' | 'error' | 'not-found' | 'ready';

export function VideoWatchPage() {
  const { videoId } = useParams<{ videoId: string }>();
  const id = Number(videoId);

  const [video, setVideo] = useState<VideoDetail | null>(null);
  const [state, setState] = useState<LoadState>('loading');

  async function load() {
    setState('loading');
    try {
      const data = await fetchVideo(id);
      setVideo(data);
      setState('ready');
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setState('not-found');
      } else {
        setState('error');
      }
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  if (state === 'loading') return <LoadingState label="Loading video…" />;
  if (state === 'not-found') {
    return <EmptyState>This video isn't available right now.</EmptyState>;
  }
  if (state === 'error' || !video) {
    return <ErrorState message="Couldn't load this video." onRetry={load} />;
  }

  return (
    <div className="flex flex-col gap-4">
      <PageHeader icon={<VideoIcon />}>{video.title}</PageHeader>

      <VideoPlayer video={video} title={video.title} />
    </div>
  );
}
