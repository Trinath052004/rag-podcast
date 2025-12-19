import React, { useState, useRef, useEffect } from 'react';
import { Play, Pause, Volume2, VolumeX, SkipBack, SkipForward, Download, Share, PlayCircle, PauseCircle } from 'lucide-react';

const PodcastPlayer = ({ podcast, onPlayPause, isPlaying }) => {
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.8);
  const [isMuted, setIsMuted] = useState(false);
  const [playbackRate, setPlaybackRate] = useState(1.0);
  const [currentSegment, setCurrentSegment] = useState(0);
  const [showAllSegments, setShowAllSegments] = useState(false);

  const audioRef = useRef(null);
  const progressBarRef = useRef(null);

  // Calculate total duration from segments
  useEffect(() => {
    if (podcast?.audio?.segments) {
      const totalDur = podcast.audio.segments.reduce((sum, segment) => sum + segment.duration, 0);
      setDuration(totalDur);
    }
  }, [podcast]);

  // Handle audio playback
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime);
    };

    const handleLoadedMetadata = () => {
      setDuration(audio.duration);
    };

    const handleEnded = () => {
      setCurrentTime(0);
      setIsPlaying(false);
      if (onPlayPause) onPlayPause(false);
    };

    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('ended', handleEnded);
    };
  }, []);

  // Sync with parent play/pause state
  useEffect(() => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.play().catch(error => {
          console.error('Audio play error:', error);
        });
      } else {
        audioRef.current.pause();
      }
    }
  }, [isPlaying]);

  const togglePlayPause = () => {
    const newState = !isPlaying;
    setIsPlaying(newState);
    if (onPlayPause) onPlayPause(newState);
  };

  const handleProgressClick = (e) => {
    if (!audioRef.current || !progressBarRef.current) return;

    const progressBar = progressBarRef.current;
    const rect = progressBar.getBoundingClientRect();
    const clickPosition = e.clientX - rect.left;
    const percentage = clickPosition / rect.width;
    const newTime = percentage * duration;

    audioRef.current.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const formatTime = (seconds) => {
    if (isNaN(seconds)) return '0:00';

    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
  };

  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
    }
    if (newVolume === 0) {
      setIsMuted(true);
    } else if (isMuted) {
      setIsMuted(false);
    }
  };

  const toggleMute = () => {
    const newMutedState = !isMuted;
    setIsMuted(newMutedState);
    if (audioRef.current) {
      audioRef.current.muted = newMutedState;
    }
  };

  const handlePlaybackRateChange = (rate) => {
    setPlaybackRate(rate);
    if (audioRef.current) {
      audioRef.current.playbackRate = rate;
    }
  };

  const handleSegmentClick = (index) => {
    setCurrentSegment(index);
    // In a real implementation, we would seek to the segment start time
    // For now, we'll just update the current segment
  };

  const handleDownload = () => {
    if (podcast?.audio?.download_url) {
      window.open(podcast.audio.download_url, '_blank');
    }
  };

  const handleShare = () => {
    if (navigator.share && podcast) {
      navigator.share({
        title: podcast.title,
        text: `Check out this podcast about ${podcast.title}`,
        url: window.location.href,
      }).catch(error => {
        console.error('Share error:', error);
      });
    } else {
      // Fallback for browsers that don't support Web Share API
      alert('Share functionality is not supported in your browser');
    }
  };

  if (!podcast) {
    return (
      <div className="podcast-player bg-gray-50 rounded-xl p-6 text-center">
        <PlayCircle className="mx-auto text-gray-300" size={48} />
        <p className="text-gray-500 mt-2">No podcast available</p>
      </div>
    );
  }

  return (
    <div className="podcast-player bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-gray-800">{podcast.title}</h3>
            <p className="text-sm text-gray-600 mt-1">
              {podcast.audio?.segments?.length || 0} segments • {formatTime(duration)}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={handleShare}
              className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg"
              title="Share podcast"
            >
              <Share size={18} />
            </button>
            <button
              onClick={handleDownload}
              className="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg"
              title="Download podcast"
            >
              <Download size={18} />
            </button>
          </div>
        </div>
      </div>

      <div className="p-4">
        <div className="audio-controls mb-4">
          <div className="flex items-center justify-center mb-4">
            <button
              onClick={togglePlayPause}
              className="w-16 h-16 bg-blue-500 text-white rounded-full flex items-center justify-center hover:bg-blue-600 transition-colors shadow-lg"
            >
              {isPlaying ? (
                <PauseCircle size={32} />
              ) : (
                <PlayCircle size={32} />
              )}
            </button>
          </div>

          <div className="flex items-center space-x-3 mb-4">
            <button
              className="p-2 text-gray-600 hover:text-gray-800"
              title="Previous segment"
              onClick={() => handleSegmentClick(Math.max(0, currentSegment - 1))}
            >
              <SkipBack size={18} />
            </button>

            <button
              className="p-2 text-gray-600 hover:text-gray-800"
              title="Next segment"
              onClick={() => handleSegmentClick(Math.min((podcast.audio?.segments?.length || 1) - 1, currentSegment + 1))}
            >
              <SkipForward size={18} />
            </button>

            <span className="text-sm text-gray-600">
              {formatTime(currentTime)} / {formatTime(duration)}
            </span>
          </div>

          <div
            ref={progressBarRef}
            className="progress-bar h-1 bg-gray-200 rounded-full cursor-pointer mb-4"
            onClick={handleProgressClick}
          >
            <div
              className="h-full bg-blue-500 rounded-full transition-all"
              style={{ width: `${(currentTime / duration) * 100}%` }}
            ></div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <button
                onClick={toggleMute}
                className="p-1 text-gray-600 hover:text-gray-800"
                title={isMuted ? 'Unmute' : 'Mute'}
              >
                {isMuted ? <VolumeX size={18} /> : <Volume2 size={18} />}
              </button>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={isMuted ? 0 : volume}
                onChange={handleVolumeChange}
                className="w-20"
              />
            </div>

            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">Speed:</span>
              {[0.5, 1.0, 1.5, 2.0].map((rate) => (
                <button
                  key={rate}
                  onClick={() => handlePlaybackRateChange(rate)}
                  className={`px-2 py-1 text-sm rounded ${
                    playbackRate === rate ? 'bg-blue-500 text-white' : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  {rate}x
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="podcast-segments mt-6">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-semibold text-gray-800">Podcast Segments</h4>
            <button
              onClick={() => setShowAllSegments(!showAllSegments)}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              {showAllSegments ? 'Show Less' : 'Show All'}
            </button>
          </div>

          <div className="space-y-2 max-h-64 overflow-y-auto">
            {(showAllSegments ? podcast.audio?.segments : podcast.audio?.segments?.slice(0, 3))?.map((segment, index) => (
              <div
                key={segment.segment_id}
                className={`segment p-3 rounded-lg cursor-pointer transition-colors ${
                  currentSegment === index
                    ? 'bg-blue-50 border-blue-200 border'
                    : 'bg-gray-50 hover:bg-gray-100'
                }`}
                onClick={() => handleSegmentClick(index)}
              >
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <Volume2 className="text-blue-600" size={16} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-800">
                        Segment {index + 1}: {segment.agent_id === 'user' ? 'Your Question' : segment.agent_id}
                      </span>
                      <span className="text-xs text-gray-500">{formatTime(segment.duration)}</span>
                    </div>
                    <p className="text-sm text-gray-600 truncate">{segment.text_content}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <audio
          ref={audioRef}
          src={podcast.audio?.segments?.[currentSegment]?.audio_url || podcast.audio?.download_url}
          onEnded={() => {
            setIsPlaying(false);
            if (onPlayPause) onPlayPause(false);
          }}
        />
      </div>
    </div>
  );
};

export default PodcastPlayer;
