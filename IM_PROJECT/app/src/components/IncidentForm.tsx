/**
 * Incident Form Component for DMMMSU-SLUC Disaster Monitoring System
 * Handles new incident submission
 */

import { useState } from 'react';
import { incidentsApi } from '@/services/api';
import { Calendar, Clock, MapPin, FileText, Upload, X, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

interface IncidentFormProps {
  onSuccess: () => void;
  onCancel: () => void;
}

export default function IncidentForm({ onSuccess, onCancel }: IncidentFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    time: new Date().toTimeString().slice(0, 5),
    location: '',
    cause: '',
    description: ''
  });
  const [file, setFile] = useState<File | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [dragActive, setDragActive] = useState(false);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.date) {
      newErrors.date = 'Date is required';
    }
    if (!formData.time) {
      newErrors.time = 'Time is required';
    }
    if (!formData.location.trim()) {
      newErrors.location = 'Location is required';
    }
    if (!formData.cause.trim()) {
      newErrors.cause = 'Cause of incident is required';
    }
    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    } else if (formData.description.length < 20) {
      newErrors.description = 'Description must be at least 20 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      toast.error('Please fill in all required fields');
      return;
    }

    setIsSubmitting(true);

    try {
      const submitData = new FormData();
      submitData.append('date', formData.date);
      submitData.append('time', formData.time);
      submitData.append('location', formData.location);
      submitData.append('cause', formData.cause);
      submitData.append('description', formData.description);
      if (file) {
        submitData.append('supporting_file', file);
      }

      await incidentsApi.create(submitData);
      onSuccess();
    } catch (error) {
      console.error('Error submitting incident:', error);
      toast.error('Failed to submit incident report');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const removeFile = () => {
    setFile(null);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Date and Time Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="date" className="text-slate-300">
            Date of Incident <span className="text-red-400">*</span>
          </Label>
          <div className="relative">
            <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
            <Input
              id="date"
              type="date"
              value={formData.date}
              onChange={(e) => handleChange('date', e.target.value)}
              className={cn(
                "pl-10 bg-slate-700/50 border-slate-600 text-white",
                errors.date && "border-red-500"
              )}
            />
          </div>
          {errors.date && <p className="text-red-400 text-xs">{errors.date}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="time" className="text-slate-300">
            Time of Incident <span className="text-red-400">*</span>
          </Label>
          <div className="relative">
            <Clock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
            <Input
              id="time"
              type="time"
              value={formData.time}
              onChange={(e) => handleChange('time', e.target.value)}
              className={cn(
                "pl-10 bg-slate-700/50 border-slate-600 text-white",
                errors.time && "border-red-500"
              )}
            />
          </div>
          {errors.time && <p className="text-red-400 text-xs">{errors.time}</p>}
        </div>
      </div>

      {/* Location */}
      <div className="space-y-2">
        <Label htmlFor="location" className="text-slate-300">
          Location <span className="text-red-400">*</span>
        </Label>
        <div className="relative">
          <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
          <Input
            id="location"
            type="text"
            placeholder="e.g., Main Building, Room 101"
            value={formData.location}
            onChange={(e) => handleChange('location', e.target.value)}
            className={cn(
              "pl-10 bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-500",
              errors.location && "border-red-500"
            )}
          />
        </div>
        {errors.location && <p className="text-red-400 text-xs">{errors.location}</p>}
      </div>

      {/* Cause */}
      <div className="space-y-2">
        <Label htmlFor="cause" className="text-slate-300">
          Cause of Incident <span className="text-red-400">*</span>
        </Label>
        <div className="relative">
          <FileText className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
          <Input
            id="cause"
            type="text"
            placeholder="e.g., Fire, Flood, Electrical Issue"
            value={formData.cause}
            onChange={(e) => handleChange('cause', e.target.value)}
            className={cn(
              "pl-10 bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-500",
              errors.cause && "border-red-500"
            )}
          />
        </div>
        {errors.cause && <p className="text-red-400 text-xs">{errors.cause}</p>}
      </div>

      {/* Description */}
      <div className="space-y-2">
        <Label htmlFor="description" className="text-slate-300">
          Detailed Description <span className="text-red-400">*</span>
        </Label>
        <Textarea
          id="description"
          placeholder="Provide a detailed description of the incident..."
          value={formData.description}
          onChange={(e) => handleChange('description', e.target.value)}
          rows={4}
          className={cn(
            "bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-500 resize-none",
            errors.description && "border-red-500"
          )}
        />
        {errors.description ? (
          <p className="text-red-400 text-xs">{errors.description}</p>
        ) : (
          <p className="text-slate-500 text-xs">
            Minimum 20 characters. Be as detailed as possible.
          </p>
        )}
      </div>

      {/* File Upload */}
      <div className="space-y-2">
        <Label className="text-slate-300">Supporting Documents (Optional)</Label>
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={cn(
            "border-2 border-dashed rounded-lg p-6 text-center transition-colors",
            dragActive
              ? "border-blue-500 bg-blue-500/10"
              : "border-slate-600 hover:border-slate-500",
            file && "border-emerald-500 bg-emerald-500/10"
          )}
        >
          {file ? (
            <div className="flex items-center justify-center gap-3">
              <div className="flex items-center gap-2">
                <Upload className="w-5 h-5 text-emerald-500" />
                <span className="text-emerald-400 text-sm">{file.name}</span>
              </div>
              <button
                type="button"
                onClick={removeFile}
                className="p-1 rounded-full hover:bg-slate-700 text-slate-400 hover:text-red-400"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <label className="cursor-pointer">
              <Upload className="w-8 h-8 mx-auto mb-2 text-slate-500" />
              <p className="text-slate-400 text-sm mb-1">
                Drag and drop files here, or click to browse
              </p>
              <p className="text-slate-500 text-xs">
                Supports: Images, PDFs, Documents (max 10MB)
              </p>
              <input
                type="file"
                onChange={handleFileChange}
                className="hidden"
                accept="image/*,.pdf,.doc,.docx"
              />
            </label>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-700">
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={isSubmitting}
          className="border-slate-600 text-slate-300 hover:bg-slate-700"
        >
          Cancel
        </Button>
        <Button
          type="submit"
          disabled={isSubmitting}
          className="bg-blue-600 hover:bg-blue-700 text-white"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Submitting...
            </>
          ) : (
            'Submit Report'
          )}
        </Button>
      </div>
    </form>
  );
}
