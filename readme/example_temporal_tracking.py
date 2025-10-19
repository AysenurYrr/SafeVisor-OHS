"""
Example usage of temporal tracking and smart violation reporting.

This example demonstrates how to use the new tracking system in a simple video processing script.
"""

import cv2
import sys
import os

# Add ppe_detection_system to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ppe_detection_system'))

from temporal_tracker import TemporalTracker
from violation_manager import ViolationManager
from detector import YoloDetector


def process_video_with_tracking(video_path: str, model_path: str):
    """
    Process a video file with temporal tracking and violation detection.
    
    Args:
        video_path: Path to video file
        model_path: Path to YOLO model
    """
    # Initialize components
    print("Initializing detector...")
    detector = YoloDetector(model_path, conf_threshold=0.6)
    
    print("Initializing temporal tracker...")
    tracker = TemporalTracker(
        max_distance=100,
        max_missing_frames=30,
        grace_frames=2,
        confidence_threshold=0.2
    )
    
    print("Initializing violation manager...")
    violation_manager = ViolationManager(
        factory_area_name="Production Floor A",
        camera_name="Main Camera",
        min_consecutive_frames=5,
        violation_timeout=5.0,
        violations_dir="violations/images"
    )
    
    # Set required PPE for this area
    violation_manager.set_required_ppe(["helmet", "safety-vest"])
    
    # Open video
    print(f"Opening video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return
    
    frame_count = 0
    total_violations = 0
    
    print("\nProcessing video...")
    print("Press 'q' to quit\n")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Detect PPE
            detections = detector.infer(frame)
            
            # Update temporal tracker
            tracked_persons = tracker.update_frame(detections)
            
            # Check for violations
            violations = violation_manager.check_violations(
                tracked_persons, frame, frame_count
            )
            
            # Log violations
            if violations:
                for violation in violations:
                    total_violations += 1
                    print(f"\n[VIOLATION #{total_violations}]")
                    print(f"  Frame: {frame_count}")
                    print(f"  Employee: {violation['employee_name']}")
                    print(f"  Type: {violation['violation_type']}")
                    print(f"  Duration: {violation['duration_frames']} frames")
                    print(f"  Confidence: {violation['confidence_score']}%")
                    print(f"  Evidence:")
                    for key, path in violation['evidence_images'].items():
                        print(f"    {key}: {path}")
            
            # Draw tracked persons
            for person in tracked_persons:
                x1, y1, x2, y2 = person.box
                
                # Color based on PPE status
                has_all_ppe = all(
                    person.get_stable_ppe_status(ppe, frame_count, grace_frames=2)
                    for ppe in ["helmet", "safety-vest"]
                )
                color = (0, 255, 0) if has_all_ppe else (0, 0, 255)
                
                # Draw box
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                # Draw label
                name = person.recognized_name or f"Person {person.person_id}"
                cv2.putText(frame, name, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                # Draw PPE status
                y_offset = y1 - 30
                for ppe_type in ["helmet", "safety-vest"]:
                    has_ppe = person.get_stable_ppe_status(ppe_type, frame_count, grace_frames=2)
                    status = "✓" if has_ppe else "✗"
                    status_color = (0, 255, 0) if has_ppe else (0, 0, 255)
                    text = f"{ppe_type}: {status}"
                    cv2.putText(frame, text, (x1, y_offset),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, status_color, 1)
                    y_offset -= 15
            
            # Display frame info
            info_text = f"Frame: {frame_count} | Persons: {len(tracked_persons)} | Violations: {total_violations}"
            cv2.putText(frame, info_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Show frame
            cv2.imshow('PPE Detection with Temporal Tracking', frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\nQuitting...")
                break
            
            # Periodic cleanup
            if frame_count % 300 == 0:  # Every 10 seconds at 30 FPS
                tracker.cleanup_old_persons(max_age_seconds=30.0)
                print(f"[Frame {frame_count}] Cleanup: {len(tracked_persons)} active persons")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
    
    # Print summary
    print("\n" + "="*60)
    print("PROCESSING SUMMARY")
    print("="*60)
    print(f"Total frames processed: {frame_count}")
    print(f"Total violations detected: {total_violations}")
    
    stats = violation_manager.get_statistics()
    print(f"\nViolation Manager Statistics:")
    print(f"  Factory Area: {stats['factory_area']}")
    print(f"  Camera: {stats['camera_name']}")
    print(f"  Required PPE: {', '.join(stats['required_ppe'])}")
    print(f"  Total reported: {stats['total_violations_reported']}")
    print(f"  Active violations: {stats['active_violations']}")
    print("="*60)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Process video with temporal tracking and violation detection'
    )
    parser.add_argument('video', help='Path to video file')
    parser.add_argument('--model', default='ppe_detection_system/models/yolo9e.pt',
                       help='Path to YOLO model (default: ppe_detection_system/models/yolo9e.pt)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.video):
        print(f"Error: Video file not found: {args.video}")
        return 1
    
    if not os.path.exists(args.model):
        print(f"Error: Model file not found: {args.model}")
        return 1
    
    try:
        process_video_with_tracking(args.video, args.model)
        return 0
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 0
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
