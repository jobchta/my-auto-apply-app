'use server'

import { createClient } from '@/utils/supabase/server'
import { revalidatePath } from 'next/cache'

export async function createApplication(jobId: number) {
  // Add the 'await' keyword here
  const supabase = await createClient()

  const { data: { user } } = await supabase.auth.getUser()
  if (!user) {
    return { error: 'You must be logged in to apply.' }
  }

  // First, check if a profile exists for this user.
  // This assumes you have a 'profiles' table linked to the 'users' table.
  const { data: profile, error: profileError } = await supabase
    .from('profiles')
    .select('id')
    .eq('id', user.id)
    .single();

  if (profileError || !profile) {
    console.error('Profile not found for user:', user.id, profileError);
    return { error: 'You must complete your profile before applying.' };
  }

  const { error } = await supabase.from('applications').insert({
    job_id: jobId,
    user_id: user.id,
  })

  if (error) {
    // Handle potential duplicate application error gracefully
    if (error.code === '23505') { // '23505' is the code for unique_violation
        return { error: 'You have already applied for this job.' };
    }
    console.error('Error creating application:', error)
    return { error: 'Could not apply for this job.' }
  }

  revalidatePath('/')
  return { success: 'Application submitted!' }
}