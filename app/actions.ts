'use server'

import { createClient } from '@/utils/supabase/server'
import { revalidatePath } from 'next/cache'

export async function createApplication(jobId: number) {
  const supabase = await createClient() // Keep await here

  const { data: { user }, error: authError } = await supabase.auth.getUser()
  if (authError || !user) {
    return { error: 'You must be logged in to apply.' }
  }

  // Check if profile exists and is complete
  const { data: profile, error: profileError } = await supabase
    .from('profiles')
    .select('id, full_name, phone, resume_url')
    .eq('id', user.id)
    .single()

  if (profileError || !profile) {
    console.error('Profile error:', profileError)
    return { error: 'Please complete your profile before applying.' }
  }

  // Verify required profile fields
  const missingFields = []
  if (!profile.full_name) missingFields.push('full name')
  if (!profile.phone) missingFields.push('phone number')
  if (!profile.resume_url) missingFields.push('resume URL')
  
  if (missingFields.length > 0) {
    return { error: `Please provide your ${missingFields.join(', ')} in your profile.` }
  }

  // Submit application
  const { error: applicationError } = await supabase
    .from('applications')
    .insert({
      job_id: jobId,
      user_id: user.id,
      applied_at: new Date().toISOString()
    })

  if (applicationError) {
    if (applicationError.code === '23505') {
      return { error: 'You have already applied to this position.' }
    }
    console.error('Application error:', applicationError)
    return { error: 'Failed to submit application. Please try again.' }
  }

  revalidatePath('/jobs')
  return { success: 'Application submitted successfully!' }
}

export async function updateProfile(formData: FormData) {
  const supabase = await createClient() // Keep await here

  const { data: { user }, error: authError } = await supabase.auth.getUser()
  if (authError || !user) {
    return { error: 'You must be logged in to update your profile.' }
  }

  const updates = {
    id: user.id,
    full_name: formData.get('fullName') as string,
    email: formData.get('email') as string,
    phone: formData.get('phone') as string,
    resume_url: formData.get('resumeUrl') as string,
    updated_at: new Date().toISOString()
  }

  const { error } = await supabase
    .from('profiles')
    .upsert(updates)

  if (error) {
    console.error('Profile update error:', error)
    return { error: 'Failed to save profile. Please try again.' }
  }

  revalidatePath('/profile')
  return { success: 'Profile updated successfully!' }
}