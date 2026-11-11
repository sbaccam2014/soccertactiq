import type { SVGProps } from 'react';

/**
 * Small inline SVG icon set, styled after catch.co's simple line icons
 * but with a bolder stroke (2.5 vs. their 2) for young-kid legibility at
 * small sizes. No icon library dependency — this is the full set the
 * app needs, so a few inline SVGs are simpler than adding one.
 */

type IconProps = SVGProps<SVGSVGElement>;

function Icon({ children, ...rest }: IconProps & { children: React.ReactNode }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2.5}
      strokeLinecap="round"
      strokeLinejoin="round"
      {...rest}
    >
      {children}
    </svg>
  );
}

export function VideoIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <rect x="2.5" y="5.5" width="14" height="13" rx="2.5" />
      <path d="M16.5 10.5l5-3v9l-5-3" />
    </Icon>
  );
}

export function LibraryIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <rect x="3" y="4" width="7" height="16" rx="1.5" />
      <rect x="14" y="4" width="7" height="16" rx="1.5" />
      <path d="M6.5 8h0M17.5 8h0" />
    </Icon>
  );
}

export function BallIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7l4 3-1.5 4.5h-5L8 10l4-3z" />
      <path d="M12 3v4M3.5 9.5L8 10M20.5 9.5L16 10M8 16.5l-3 3M16 16.5l3 3M12 21v-4" />
    </Icon>
  );
}

export function ChartIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <path d="M4 20V10M12 20V4M20 20v-7" />
      <path d="M2 20h20" />
    </Icon>
  );
}

export function PeopleIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <circle cx="9" cy="8" r="3.25" />
      <path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6" />
      <circle cx="17.5" cy="9" r="2.5" />
      <path d="M15.8 14.3c2.5.4 4.2 2.6 4.2 5.2" />
    </Icon>
  );
}

export function PersonIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <circle cx="12" cy="8" r="4" />
      <path d="M4 20.5c0-4.4 3.6-8 8-8s8 3.6 8 8" />
    </Icon>
  );
}

export function AddVideoIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <rect x="2.5" y="5.5" width="13" height="13" rx="2.5" />
      <path d="M9 9v5M6.5 11.5h5" />
      <path d="M16.5 10.5l5-3v9l-5-3" />
    </Icon>
  );
}

export function CheckIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <path d="M5 13l4.5 4.5L19 7.5" />
    </Icon>
  );
}

export function XIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <path d="M6 6l12 12M18 6L6 18" />
    </Icon>
  );
}

export function FlameIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <path d="M12 2.5c1 3 .3 4.3-1 6-1.7 2.1-3 3.8-3 6.3a4 4 0 008 0c0-1.5-.6-2.4-1.3-3.4 1.6.4 2.8 2.1 2.8 4.2a5.5 5.5 0 01-11 0c0-5.8 5.5-8 5.5-13.1z" />
    </Icon>
  );
}

export function PlayIcon(props: IconProps) {
  return (
    <Icon {...props} fill="currentColor" stroke="none">
      <path d="M8 5.5v13l11-6.5-11-6.5z" />
    </Icon>
  );
}

export function InfoIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 11v6M12 7.5h0" />
    </Icon>
  );
}

export function TargetIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <circle cx="12" cy="12" r="8.5" />
      <circle cx="12" cy="12" r="4.5" />
      <circle cx="12" cy="12" r="1" fill="currentColor" stroke="none" />
    </Icon>
  );
}

export function ShieldIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <path d="M12 3l7 3v5.5c0 4.5-3 7.8-7 9.5-4-1.7-7-5-7-9.5V6l7-3z" />
    </Icon>
  );
}

export function EyeIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <path d="M2.5 12S5.8 5.5 12 5.5 21.5 12 21.5 12 18.2 18.5 12 18.5 2.5 12 2.5 12z" />
      <circle cx="12" cy="12" r="3" />
    </Icon>
  );
}

export function EyeOffIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <path d="M3.5 3.5l17 17" />
      <path d="M10.6 5.6A10.6 10.6 0 0112 5.5c6.2 0 9.5 6.5 9.5 6.5a16.4 16.4 0 01-3.2 4.2M6.8 7.4A16.5 16.5 0 002.5 12S5.8 18.5 12 18.5a10.4 10.4 0 004.2-.9" />
      <path d="M9.9 9.9a3 3 0 004.2 4.2" />
    </Icon>
  );
}
