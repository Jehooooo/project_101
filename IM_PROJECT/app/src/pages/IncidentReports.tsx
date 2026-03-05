/**
 * Incident Reports Page for DMMMSU-SLUC Disaster Monitoring System
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { incidentsApi } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import type { Incident, IncidentFilters } from '@/types';
import {
  Search, Download, Eye, ChevronLeft, ChevronRight, Calendar, MapPin, User,
  RefreshCw, Loader2, FileText, CheckCircle2, X, Clock
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription,
} from '@/components/ui/dialog';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.05 } }
};

const itemVariants = {
  hidden: { opacity: 0, y: 10 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3 } }
};

export default function IncidentReports() {
  const { user, hasRole } = useAuth();
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filters, setFilters] = useState<IncidentFilters>({
    status: '', location: '', date_from: '', date_to: '', search: ''
  });
  const [pagination, setPagination] = useState({
    page: 1, per_page: 10, total: 0, pages: 0
  });
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);

  useEffect(() => { fetchIncidents(); }, [pagination.page, filters]);

  const fetchIncidents = async () => {
    try {
      setIsLoading(true);
      const response = await incidentsApi.getAll({
        ...filters, page: pagination.page, per_page: pagination.per_page
      });
      setIncidents(response.incidents);
      setPagination(prev => ({ ...prev, total: response.total, pages: response.pages }));
    } catch (error) {
      toast.error('Failed to load incidents');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handleClearFilters = () => {
    setFilters({ status: '', location: '', date_from: '', date_to: '', search: '' });
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handleViewDetail = (incident: Incident) => {
    setSelectedIncident(incident);
    setIsDetailOpen(true);
  };

  const handleDownloadPdf = async (incidentId: number, e?: React.MouseEvent) => {
    e?.stopPropagation();
    try {
      toast.info('Downloading PDF...');
      await incidentsApi.downloadPdf(incidentId);
      toast.success('PDF downloaded successfully');
    } catch (error) {
      toast.error('Failed to download PDF');
    }
  };

  const handleStatusUpdate = async (incidentId: number, newStatus: string) => {
    try {
      await incidentsApi.updateStatus(incidentId, newStatus);
      toast.success(`Status updated to ${newStatus}`);
      fetchIncidents();
      if (selectedIncident && selectedIncident.id === incidentId) {
        setSelectedIncident({ ...selectedIncident, status: newStatus as any });
      }
    } catch (error) {
      toast.error('Failed to update status');
    }
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'Pending': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'In Progress': return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
      case 'Solved': return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
      default: return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
    }
  };

  const hasActiveFilters = Object.values(filters).some(v => v !== '');

  return (
    <motion.div variants={containerVariants} initial="hidden" animate="visible" className="space-y-6">
      <motion.div variants={itemVariants} className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Incident Reports</h1>
          <p className="text-slate-400 mt-1">View and manage all incident reports</p>
        </div>
        <Button variant="outline" size="sm" onClick={fetchIncidents} disabled={isLoading}
          className="border-slate-600 text-slate-300 hover:bg-slate-700">
          <RefreshCw className={cn("w-4 h-4 mr-2", isLoading && "animate-spin")} />
          Refresh
        </Button>
      </motion.div>

      <motion.div variants={itemVariants}>
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-4">
            <div className="flex flex-col lg:flex-row gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <Input placeholder="Search by location, cause, or description..." value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  className="pl-10 bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-500" />
              </div>
              <Select value={filters.status} onValueChange={(v) => handleFilterChange('status', v)}>
                <SelectTrigger className="w-full lg:w-[180px] bg-slate-700/50 border-slate-600 text-white">
                  <SelectValue placeholder="All Statuses" />
                </SelectTrigger>
                <SelectContent className="bg-slate-800 border-slate-700">
                  <SelectItem value="">All Statuses</SelectItem>
                  <SelectItem value="Pending">Pending</SelectItem>
                  <SelectItem value="In Progress">In Progress</SelectItem>
                  <SelectItem value="Solved">Solved</SelectItem>
                </SelectContent>
              </Select>
              <div className="flex items-center gap-2">
                <Input type="date" value={filters.date_from}
                  onChange={(e) => handleFilterChange('date_from', e.target.value)}
                  className="w-full lg:w-[140px] bg-slate-700/50 border-slate-600 text-white" />
                <span className="text-slate-500">to</span>
                <Input type="date" value={filters.date_to}
                  onChange={(e) => handleFilterChange('date_to', e.target.value)}
                  className="w-full lg:w-[140px] bg-slate-700/50 border-slate-600 text-white" />
              </div>
              {hasActiveFilters && (
                <Button variant="ghost" size="sm" onClick={handleClearFilters} className="text-slate-400 hover:text-white">
                  <X className="w-4 h-4 mr-1" /> Clear
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div variants={itemVariants}>
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-white text-lg">
              All Incidents <span className="ml-2 text-sm text-slate-400">({pagination.total} total)</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
              </div>
            ) : incidents.length === 0 ? (
              <div className="text-center py-12 text-slate-500">
                <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p className="text-lg font-medium mb-2">No incidents found</p>
                <p className="text-sm">Try adjusting your filters</p>
              </div>
            ) : (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-slate-700">
                        <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">ID</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">Date & Time</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">Location</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">Cause</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">Status</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">Reported By</th>
                        <th className="text-right py-3 px-4 text-sm font-medium text-slate-400">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {incidents.map((incident, index) => (
                        <motion.tr key={incident.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                          transition={{ delay: index * 0.05 }}
                          className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors cursor-pointer"
                          onClick={() => handleViewDetail(incident)}>
                          <td className="py-3 px-4 text-sm text-slate-300 font-mono">{incident.incident_id}</td>
                          <td className="py-3 px-4 text-sm text-slate-300">
                            <div>{incident.date}</div>
                            <div className="text-slate-500 text-xs">{incident.time}</div>
                          </td>
                          <td className="py-3 px-4 text-sm text-slate-300 max-w-[150px] truncate">{incident.location}</td>
                          <td className="py-3 px-4 text-sm text-slate-300 max-w-[150px] truncate">{incident.cause}</td>
                          <td className="py-3 px-4">
                            <Badge variant="outline" className={getStatusBadgeClass(incident.status)}>
                              {incident.status}
                            </Badge>
                          </td>
                          <td className="py-3 px-4 text-sm text-slate-300">{incident.reporter_name}</td>
                          <td className="py-3 px-4 text-right">
                            <div className="flex items-center justify-end gap-1">
                              <Button variant="ghost" size="sm"
                                onClick={(e) => { e.stopPropagation(); handleViewDetail(incident); }}
                                className="text-slate-400 hover:text-blue-400 hover:bg-blue-500/10">
                                <Eye className="w-4 h-4" />
                              </Button>
                              <Button variant="ghost" size="sm"
                                onClick={(e) => handleDownloadPdf(incident.id, e)}
                                className="text-slate-400 hover:text-emerald-400 hover:bg-emerald-500/10">
                                <Download className="w-4 h-4" />
                              </Button>
                            </div>
                          </td>
                        </motion.tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="flex items-center justify-between mt-6 pt-4 border-t border-slate-700">
                  <p className="text-sm text-slate-400">
                    Showing {((pagination.page - 1) * pagination.per_page) + 1} to{' '}
                    {Math.min(pagination.page * pagination.per_page, pagination.total)} of {pagination.total} results
                  </p>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm"
                      onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
                      disabled={pagination.page === 1}
                      className="border-slate-600 text-slate-300 hover:bg-slate-700 disabled:opacity-50">
                      <ChevronLeft className="w-4 h-4" />
                    </Button>
                    <span className="text-sm text-slate-400 px-2">Page {pagination.page} of {pagination.pages}</span>
                    <Button variant="outline" size="sm"
                      onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
                      disabled={pagination.page === pagination.pages}
                      className="border-slate-600 text-slate-300 hover:bg-slate-700 disabled:opacity-50">
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </motion.div>

      <Dialog open={isDetailOpen} onOpenChange={setIsDetailOpen}>
        <DialogContent className="max-w-2xl bg-slate-800 border-slate-700 text-white max-h-[90vh] overflow-y-auto">
          {selectedIncident && (
            <>
              <DialogHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <DialogTitle className="text-xl">{selectedIncident.incident_id}</DialogTitle>
                    <DialogDescription className="text-slate-400">Incident Details</DialogDescription>
                  </div>
                  <Badge variant="outline" className={getStatusBadgeClass(selectedIncident.status)}>
                    {selectedIncident.status}
                  </Badge>
                </div>
              </DialogHeader>
              <div className="space-y-6 mt-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 rounded-lg bg-slate-700/50">
                    <p className="text-xs text-slate-500 mb-1">Date</p>
                    <div className="flex items-center gap-2 text-slate-200">
                      <Calendar className="w-4 h-4 text-slate-400" />{selectedIncident.date}
                    </div>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-700/50">
                    <p className="text-xs text-slate-500 mb-1">Time</p>
                    <div className="flex items-center gap-2 text-slate-200">
                      <Clock className="w-4 h-4 text-slate-400" />{selectedIncident.time}
                    </div>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-700/50 col-span-2">
                    <p className="text-xs text-slate-500 mb-1">Location</p>
                    <div className="flex items-center gap-2 text-slate-200">
                      <MapPin className="w-4 h-4 text-slate-400" />{selectedIncident.location}
                    </div>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-700/50 col-span-2">
                    <p className="text-xs text-slate-500 mb-1">Cause</p>
                    <div className="flex items-center gap-2 text-slate-200">
                      <FileText className="w-4 h-4 text-slate-400" />{selectedIncident.cause}
                    </div>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-700/50 col-span-2">
                    <p className="text-xs text-slate-500 mb-1">Reported By</p>
                    <div className="flex items-center gap-2 text-slate-200">
                      <User className="w-4 h-4 text-slate-400" />{selectedIncident.reporter_name}
                    </div>
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-slate-300 mb-2">Description</h4>
                  <div className="p-4 rounded-lg bg-slate-700/50 text-slate-300 text-sm whitespace-pre-wrap">
                    {selectedIncident.description}
                  </div>
                </div>
                {selectedIncident.supporting_file && (
                  <div>
                    <h4 className="text-sm font-medium text-slate-300 mb-2">Supporting Document</h4>
                    <div className="flex items-center gap-3 p-3 rounded-lg bg-slate-700/50">
                      <FileText className="w-5 h-5 text-blue-400" />
                      <span className="text-sm text-slate-300 flex-1">
                        {selectedIncident.supporting_file.split('/').pop()}
                      </span>
                      <Button variant="ghost" size="sm" className="text-blue-400 hover:text-blue-300">
                        <Download className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                )}
                <div className="flex items-center justify-between pt-4 border-t border-slate-700">
                  <div className="flex items-center gap-2">
                    {hasRole('admin') && selectedIncident.status === 'Pending' && (
                      <Button onClick={() => handleStatusUpdate(selectedIncident.id, 'In Progress')}
                        className="bg-amber-600 hover:bg-amber-700 text-white">
                        <Clock className="w-4 h-4 mr-2" /> Mark In Progress
                      </Button>
                    )}
                    {hasRole('staff') && selectedIncident.status === 'In Progress' && 
                     selectedIncident.reported_by === user?.id && (
                      <Button onClick={() => handleStatusUpdate(selectedIncident.id, 'Solved')}
                        className="bg-emerald-600 hover:bg-emerald-700 text-white">
                        <CheckCircle2 className="w-4 h-4 mr-2" /> Mark Solved
                      </Button>
                    )}
                  </div>
                  <Button variant="outline" onClick={() => handleDownloadPdf(selectedIncident.id)}
                    className="border-slate-600 text-slate-300 hover:bg-slate-700">
                    <Download className="w-4 h-4 mr-2" /> Download PDF
                  </Button>
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </motion.div>
  );
}
