/**
 * Settings Page for DMMMSU-SLUC Disaster Monitoring System
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import {
  User, Lock, Bell, Moon, Sun, Shield, Mail, Smartphone, Save, Loader2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4 } }
};

export default function Settings() {
  const { user } = useAuth();
  const { isDarkMode, toggleTheme } = useTheme();
  const [isSaving, setIsSaving] = useState(false);
  const [profileData, setProfileData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    phone: user?.phone || ''
  });
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [notifications, setNotifications] = useState({
    email_alerts: true,
    sms_alerts: false,
    status_updates: true,
    weekly_reports: true
  });

  const handleSaveProfile = async () => {
    setIsSaving(true);
    setTimeout(() => {
      toast.success('Profile updated successfully');
      setIsSaving(false);
    }, 1000);
  };

  const handleChangePassword = async () => {
    if (passwordData.new_password !== passwordData.confirm_password) {
      toast.error('Passwords do not match');
      return;
    }
    setIsSaving(true);
    setTimeout(() => {
      toast.success('Password changed successfully');
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
      setIsSaving(false);
    }, 1000);
  };

  return (
    <motion.div variants={containerVariants} initial="hidden" animate="visible" className="space-y-6">
      <motion.div variants={itemVariants}>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-slate-400 mt-1">Manage your account and system preferences</p>
      </motion.div>

      <motion.div variants={itemVariants}>
        <Tabs defaultValue="profile" className="w-full">
          <TabsList className="bg-slate-800 border border-slate-700 mb-6">
            <TabsTrigger value="profile" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white">
              <User className="w-4 h-4 mr-2" /> Profile
            </TabsTrigger>
            <TabsTrigger value="security" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white">
              <Lock className="w-4 h-4 mr-2" /> Security
            </TabsTrigger>
            <TabsTrigger value="notifications" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white">
              <Bell className="w-4 h-4 mr-2" /> Notifications
            </TabsTrigger>
            <TabsTrigger value="appearance" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white">
              <Moon className="w-4 h-4 mr-2" /> Appearance
            </TabsTrigger>
          </TabsList>

          <TabsContent value="profile" className="mt-0">
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Profile Information</CardTitle>
                <CardDescription className="text-slate-400">Update your personal details</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="text-slate-300">First Name</Label>
                    <Input value={profileData.first_name}
                      onChange={(e) => setProfileData({ ...profileData, first_name: e.target.value })}
                      className="bg-slate-700/50 border-slate-600 text-white" />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-slate-300">Last Name</Label>
                    <Input value={profileData.last_name}
                      onChange={(e) => setProfileData({ ...profileData, last_name: e.target.value })}
                      className="bg-slate-700/50 border-slate-600 text-white" />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-300">Email Address</Label>
                  <Input type="email" value={profileData.email}
                    onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                    className="bg-slate-700/50 border-slate-600 text-white" />
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-300">Phone Number</Label>
                  <Input value={profileData.phone}
                    onChange={(e) => setProfileData({ ...profileData, phone: e.target.value })}
                    className="bg-slate-700/50 border-slate-600 text-white" placeholder="+63 XXX XXX XXXX" />
                </div>
                <div className="pt-4">
                  <Button onClick={handleSaveProfile} disabled={isSaving}
                    className="bg-blue-600 hover:bg-blue-700 text-white">
                    {isSaving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                    Save Changes
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="security" className="mt-0">
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Change Password</CardTitle>
                <CardDescription className="text-slate-400">Update your password to keep your account secure</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label className="text-slate-300">Current Password</Label>
                  <Input type="password" value={passwordData.current_password}
                    onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
                    className="bg-slate-700/50 border-slate-600 text-white" />
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-300">New Password</Label>
                  <Input type="password" value={passwordData.new_password}
                    onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                    className="bg-slate-700/50 border-slate-600 text-white" />
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-300">Confirm New Password</Label>
                  <Input type="password" value={passwordData.confirm_password}
                    onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
                    className="bg-slate-700/50 border-slate-600 text-white" />
                </div>
                <div className="pt-4">
                  <Button onClick={handleChangePassword} disabled={isSaving}
                    className="bg-blue-600 hover:bg-blue-700 text-white">
                    {isSaving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Lock className="w-4 h-4 mr-2" />}
                    Change Password
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="notifications" className="mt-0">
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Notification Preferences</CardTitle>
                <CardDescription className="text-slate-400">Choose how you want to be notified</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-4 rounded-lg bg-slate-700/50">
                  <div className="flex items-center gap-3">
                    <Mail className="w-5 h-5 text-blue-400" />
                    <div>
                      <p className="text-slate-200 font-medium">Email Alerts</p>
                      <p className="text-slate-400 text-sm">Receive email notifications for new incidents</p>
                    </div>
                  </div>
                  <Switch checked={notifications.email_alerts}
                    onCheckedChange={(v) => setNotifications({ ...notifications, email_alerts: v })} />
                </div>
                <div className="flex items-center justify-between p-4 rounded-lg bg-slate-700/50">
                  <div className="flex items-center gap-3">
                    <Smartphone className="w-5 h-5 text-emerald-400" />
                    <div>
                      <p className="text-slate-200 font-medium">SMS Alerts</p>
                      <p className="text-slate-400 text-sm">Receive SMS notifications for urgent incidents</p>
                    </div>
                  </div>
                  <Switch checked={notifications.sms_alerts}
                    onCheckedChange={(v) => setNotifications({ ...notifications, sms_alerts: v })} />
                </div>
                <div className="flex items-center justify-between p-4 rounded-lg bg-slate-700/50">
                  <div className="flex items-center gap-3">
                    <Bell className="w-5 h-5 text-amber-400" />
                    <div>
                      <p className="text-slate-200 font-medium">Status Updates</p>
                      <p className="text-slate-400 text-sm">Get notified when incident status changes</p>
                    </div>
                  </div>
                  <Switch checked={notifications.status_updates}
                    onCheckedChange={(v) => setNotifications({ ...notifications, status_updates: v })} />
                </div>
                <div className="flex items-center justify-between p-4 rounded-lg bg-slate-700/50">
                  <div className="flex items-center gap-3">
                    <Shield className="w-5 h-5 text-purple-400" />
                    <div>
                      <p className="text-slate-200 font-medium">Weekly Reports</p>
                      <p className="text-slate-400 text-sm">Receive weekly summary reports</p>
                    </div>
                  </div>
                  <Switch checked={notifications.weekly_reports}
                    onCheckedChange={(v) => setNotifications({ ...notifications, weekly_reports: v })} />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="appearance" className="mt-0">
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Appearance</CardTitle>
                <CardDescription className="text-slate-400">Customize the look and feel of the application</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-4 rounded-lg bg-slate-700/50">
                  <div className="flex items-center gap-3">
                    {isDarkMode ? <Moon className="w-5 h-5 text-indigo-400" /> : <Sun className="w-5 h-5 text-amber-400" />}
                    <div>
                      <p className="text-slate-200 font-medium">Dark Mode</p>
                      <p className="text-slate-400 text-sm">Toggle between dark and light theme</p>
                    </div>
                  </div>
                  <Switch checked={isDarkMode} onCheckedChange={toggleTheme} />
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </motion.div>
    </motion.div>
  );
}
