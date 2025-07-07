// A helper function to format the date
function timeAgo(dateString: string) {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    let interval = seconds / 31536000;
    if (interval > 1) return Math.floor(interval) + " years ago";
    interval = seconds / 2592000;
    if (interval > 1) return Math.floor(interval) + " months ago";
    interval = seconds / 86400;
    if (interval > 1) return Math.floor(interval) + " days ago";
    interval = seconds / 3600;
    if (interval > 1) return Math.floor(interval) + " hours ago";
    interval = seconds / 60;
    if (interval > 1) return Math.floor(interval) + " minutes ago";
    return Math.floor(seconds) + " seconds ago";
}

// Define the type for a single job from our database
export type Job = {
  id: number;
  created_at: string;
  title: string | null;
  company: string | null;
  location: string | null;
  url: string | null;
  source: string | null;
  description: string | null;
}

export default function JobCard({ job }: { job: Job }) {
  return (
    <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 flex justify-between items-center hover:bg-gray-700 transition-colors duration-200">
      <div>
        <h3 className="text-lg font-bold text-white">{job.title || 'No Title'}</h3>
        <p className="text-gray-400">{job.company || 'No Company'} - {job.location || 'No Location'}</p>
        <p className="text-sm text-gray-500 mt-1">
            Found {timeAgo(job.created_at)} via {job.source || 'Unknown'}
        </p>
      </div>
      <div>
        <a 
          href={job.url || '#'} 
          target="_blank" 
          rel="noopener noreferrer" 
          className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded-md"
        >
          View & Apply
        </a>
      </div>
    </div>
  )
}