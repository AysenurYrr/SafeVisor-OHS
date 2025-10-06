import React from 'react'
import {
  // Common icons
  HomeIcon,
  UserGroupIcon,
  VideoCameraIcon,
  ExclamationTriangleIcon,
  ShieldCheckIcon,
  ChartBarIcon,
  Cog6ToothIcon as CogIcon,
  BellIcon,
  UserCircleIcon,
  MagnifyingGlassIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
  ChevronDownIcon,
  ChevronRightIcon,
  ChevronLeftIcon,
  CheckCircleIcon,
  ClockIcon,
  InformationCircleIcon,
  ExclamationCircleIcon,
  PlayIcon,
  StopIcon,
  // Dashboard icons
  UserIcon,
  BuildingOfficeIcon,
  CalendarIcon,
  DocumentTextIcon,
  TagIcon,
  // Status icons
  SignalIcon,
  WifiIcon,
  BoltIcon,
  HeartIcon,
} from '@heroicons/react/24/outline'

import {
  // Solid versions for filled states
  HomeIcon as HomeSolid,
  UserGroupIcon as UserGroupSolid,
  VideoCameraIcon as VideoCameraSolid,
  ExclamationTriangleIcon as ExclamationTriangleSolid,
  ShieldCheckIcon as ShieldCheckSolid,
  ChartBarIcon as ChartBarSolid,
  CheckCircleIcon as CheckCircleSolid,
  ClockIcon as ClockSolid,
  InformationCircleIcon as InformationCircleSolid,
} from '@heroicons/react/24/solid'

const iconMap = {
  // Navigation
  home: HomeIcon,
  'home-solid': HomeSolid,
  employees: UserGroupIcon,
  'employees-solid': UserGroupSolid,
  cameras: VideoCameraIcon,
  'cameras-solid': VideoCameraSolid,
  violations: ExclamationTriangleIcon,
  'violations-solid': ExclamationTriangleSolid,
  safety: ShieldCheckIcon,
  'safety-solid': ShieldCheckSolid,
  dashboard: ChartBarIcon,
  'dashboard-solid': ChartBarSolid,
  settings: CogIcon,
  
  // Actions
  search: MagnifyingGlassIcon,
  add: PlusIcon,
  plus: PlusIcon,
  edit: PencilIcon,
  delete: TrashIcon,
  trash: TrashIcon,
  view: EyeIcon,
  logout: ArrowRightOnRectangleIcon,
  menu: Bars3Icon,
  close: XMarkIcon,
  
  // UI
  'chevron-down': ChevronDownIcon,
  'chevron-right': ChevronRightIcon,
  'chevron-left': ChevronLeftIcon,
  bell: BellIcon,
  user: UserCircleIcon,
  
  // Status
  check: CheckCircleIcon,
  'check-solid': CheckCircleSolid,
  clock: ClockIcon,
  'clock-solid': ClockSolid,
  info: InformationCircleIcon,
  'info-solid': InformationCircleSolid,
  alert: ExclamationCircleIcon,
  play: PlayIcon,
  stop: StopIcon,
  
  // Data
  person: UserIcon,
  building: BuildingOfficeIcon,
  calendar: CalendarIcon,
  document: DocumentTextIcon,
  tag: TagIcon,
  
  // System
  signal: SignalIcon,
  wifi: WifiIcon,
  bolt: BoltIcon,
  heart: HeartIcon,
}

export default function Icon({ name, className = "w-5 h-5", ...props }) {
  const IconComponent = iconMap[name]
  
  if (!IconComponent) {
    console.warn(`Icon "${name}" not found`)
    return null
  }
  
  return <IconComponent className={className} {...props} />
}

// Export individual icons for direct use
export { iconMap }