import { useState, useEffect } from "react";
import { useTasks } from "../../context/TaskContext";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Settings, Save, AlertCircle } from "lucide-react";
import toast from "react-hot-toast";
import { SettingsSkeleton } from "../../components/dashboard/SettingsSkeleton";

export function SettingsView() {
  const { token, currentStudent } = useTasks();
  const [preference, setPreference] = useState("auto");
  const [draftPreference, setDraftPreference] = useState("auto");
  const [showConfirm, setShowConfirm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPreference = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/students/me/preferences`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        const data = await response.json();
        if (data.success) {
          const pref = data.nudge_preference || "auto";
          setPreference(pref);
          setDraftPreference(pref);
        }
      } catch (e) {
        console.error(e);
        toast.error("Failed to load preferences");
      } finally {
        setLoading(false);
      }
    };
    if (token) fetchPreference();
  }, [token]);

  const savePreference = async () => {
    setSaving(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/students/me/preferences`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ nudge_preference: draftPreference })
      });
      const data = await response.json();
      if (data.success) {
        setPreference(draftPreference);
        toast.success("Preferences updated!");
        setShowConfirm(false);
      } else {
        toast.error("Failed to update preferences");
      }
    } catch (e) {
      console.error(e);
      toast.error("Network error");
    } finally {
      setSaving(false);
    }
  };

  const options = [
    { value: "auto", label: "Auto (AI Determined)", desc: "Let the AI decide what motivates you best based on risk." },
    { value: "loss_aversion", label: "Loss Aversion", desc: "Focuses on streaks and points you might lose if you procrastinate." },
    { value: "social_accountability", label: "Social Accountability", desc: "Reminds you of your promises to your buddy and the penalties." },
  ];

  if (loading) {
    return <SettingsSkeleton />;
  }

  const getLabelForValue = (val: string) => {
    return options.find(o => o.value === val)?.label || val;
  };

  return (
    <div className="p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="text-indigo-600" />
            Settings
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div>
              <h3 className="text-md font-semibold text-gray-600 mb-4">Nudge Preferences</h3>
              
              <div className="space-y-4">
                {options.map(opt => (
                  <div 
                    key={opt.value}
                    onClick={() => setDraftPreference(opt.value)}
                    className={`p-4 rounded-2xl border cursor-pointer transition-all duration-200 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 ${
                      draftPreference === opt.value 
                        ? 'border-indigo-600 bg-indigo-50/50' 
                        : 'border-transparent bg-gray-50 hover:bg-gray-100'
                    }`}
                  >
                    <div>
                      <span className={`font-semibold text-sm ${draftPreference === opt.value ? 'text-indigo-900' : 'text-gray-900'}`}>
                        {opt.label}
                      </span>
                      <p className={`mt-1 text-xs ${draftPreference === opt.value ? 'text-indigo-700/80' : 'text-gray-500'}`}>
                        {opt.desc}
                      </p>
                    </div>
                    <div className="flex-shrink-0">
                      <div className={`w-3 h-3 rounded-full border-2 flex items-center justify-center ${
                        draftPreference === opt.value ? 'border-indigo-600' : 'border-gray-300'
                      }`}>
                        {draftPreference === opt.value && <div className="w-3 h-3 rounded-full bg-indigo-600" />}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-6 border-t border-gray-100">
              <h3 className="text-md font-semibold text-gray-600 mb-4">Connected Platforms</h3>
              <div className="space-y-4">
                <div className="p-4 rounded-2xl border border-gray-200 bg-white flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center flex-shrink-0">
                      <span className="text-blue-600 font-bold text-xl">G</span>
                    </div>
                    <div>
                      <span className="font-semibold text-sm text-gray-900">Google Classroom</span>
                      <p className="mt-1 text-xs text-gray-500">Automatically sync your assignments and due dates.</p>
                    </div>
                  </div>
                  {currentStudent?.is_google_connected ? (
                    <Button 
                      variant="outline" 
                      className="flex-shrink-0 border-green-200 text-green-700 bg-green-50"
                      disabled
                    >
                      Connected
                    </Button>
                  ) : (
                    <Button 
                      variant="outline" 
                      className="flex-shrink-0 border-indigo-200 text-indigo-700 hover:bg-indigo-50"
                      onClick={() => {
                          window.location.href = `${import.meta.env.VITE_API_URL}/api/v1/auth/google`;
                      }}
                    >
                      Sync Account
                    </Button>
                  )}
                </div>
                
                <div className="p-4 rounded-2xl border border-gray-200 bg-white flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-orange-50 flex items-center justify-center flex-shrink-0">
                      <span className="text-orange-600 font-bold text-xl">M</span>
                    </div>
                    <div>
                      <span className="font-semibold text-sm text-gray-900">Moodle</span>
                      <p className="mt-1 text-xs text-gray-500">Coming soon! Bring your university tasks into RemindAI.</p>
                    </div>
                  </div>
                  <Button variant="outline" disabled className="flex-shrink-0">
                    Coming Soon
                  </Button>
                </div>
              </div>
            </div>

          </div>
        </CardContent>
        <CardFooter className="flex justify-end gap-3 border-t bg-gray-50/50 p-6 rounded-b-xl">
          {draftPreference !== preference && (
            <Button variant="ghost" onClick={() => setDraftPreference(preference)}>
              Discard Changes
            </Button>
          )}
          <Button 
            disabled={draftPreference === preference || saving} 
            onClick={() => setShowConfirm(true)}
            className="bg-indigo-600 hover:bg-indigo-700"
          >
            <Save className="w-4 h-4 mr-2" />
            Apply Settings
          </Button>
        </CardFooter>
      </Card>

      {/* CONFIRMATION MODAL */}
      {showConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="max-w-md w-full animate-in fade-in zoom-in duration-200">
            <CardHeader>
              <CardTitle className="text-indigo-600 flex items-center gap-2">
                <AlertCircle /> Confirm Preference Change
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-gray-600">
                Are you sure you want to change your motivation style?
              </p>
              <div className="bg-indigo-50 p-4 rounded-lg border border-indigo-100 text-sm text-indigo-900 space-y-2">
                <div className="flex justify-between border-b border-indigo-200 pb-2">
                  <span className="font-semibold text-gray-500">Current AI Profile:</span>
                  <span className="font-bold">{getLabelForValue(preference)}</span>
                </div>
                <div className="flex justify-between pt-1">
                  <span className="font-semibold text-gray-500">New AI Profile:</span>
                  <span className="font-bold text-indigo-700">{getLabelForValue(draftPreference)}</span>
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex justify-end gap-3 pt-4">
              <Button variant="ghost" disabled={saving} onClick={() => setShowConfirm(false)}>
                Cancel
              </Button>
              <Button onClick={savePreference} disabled={saving} className="bg-indigo-600 hover:bg-indigo-700">
                {saving ? "Saving..." : "Yes, Change It"}
              </Button>
            </CardFooter>
          </Card>
        </div>
      )}
    </div>
  );
}
