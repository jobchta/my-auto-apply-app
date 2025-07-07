import { createClient } from "@/utils/supabase/server";
import DashboardLayout from "@/components/dashboard/DashboardLayout";
import { AuthButton } from "@/components/AuthButton";
import { updateProfile } from "@/app/actions";

export default async function ProfilePage() {
  const supabase = await createClient();

  const { data: { user } } = await supabase.auth.getUser();

  // Fetch the user's profile data
  const { data: profile } = await supabase
    .from('profiles')
    .select('*')
    .single();

  return (
    <DashboardLayout>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Your Profile</h1>
        <AuthButton />
      </div>

      <div className="bg-gray-800 p-8 rounded-lg">
        <p className="text-gray-400 mb-8">
          This information will be used by the bot to auto-apply for jobs.
        </p>

        {/* The form now calls the updateProfile server action */}
        <form method="post" action="/api/update-profile" className="space-y-6">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">Email</label>
            <input 
              type="email" 
              name="email" 
              id="email" 
              defaultValue={profile?.email || ''} 
              disabled 
              className="w-full bg-gray-900 border border-gray-700 rounded-md shadow-sm py-2 px-3 text-gray-400" 
            />
          </div>
          <div>
            <label htmlFor="fullName" className="block text-sm font-medium text-gray-300 mb-2">Full Name</label>
            <input 
              type="text" 
              name="fullName" 
              id="fullName" 
              defaultValue={profile?.full_name || ''} 
              className="w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" 
            />
          </div>
          <div>
            <label htmlFor="phone" className="block text-sm font-medium text-gray-300 mb-2">Phone Number</label>
            <input 
              type="text" 
              name="phone" 
              id="phone" 
              defaultValue={profile?.phone || ''} 
              className="w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" 
            />
          </div>
           <div>
            <label htmlFor="resumeUrl" className="block text-sm font-medium text-gray-300 mb-2">Resume URL (must be a public link)</label>
            <input 
              type="text" 
              name="resumeUrl" 
              id="resumeUrl" 
              defaultValue={profile?.resume_url || ''} 
              className="w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm py-2 px-3 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" 
            />
          </div>
          <div className="mt-8">
            <button 
              type="submit" 
              className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded-md shadow-md transition-colors duration-200"
            >
              Save Profile
            </button>
          </div>
        </form>
      </div>
    </DashboardLayout>
  );
}