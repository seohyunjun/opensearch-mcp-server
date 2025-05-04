import logging
from typing import Dict, Any
from ...es_client import OpensearchClient
from mcp.types import TextContent

class AdminClusterTools(OpensearchClient):
    def register_tools(self, mcp: Any):
        """Register administrative cluster related tools."""
        
        @mcp.tool(description="Check hot threads on nodes")
        async def get_hot_threads() -> list[TextContent]:
            """
            Get hot threads information from all nodes, filtering for CPU percentage data.
            Returns only thread information containing percentage signs, indicating CPU usage.
            If no threads show percentage usage, indicates no hot threads were found.
            """
            self.logger.info("Fetching hot threads information...")
            try:
                response = self.es_client.transport.perform_request(
                    'GET',
                    '/_nodes/hot_threads'
                )
                # Filter lines containing '%'
                hot_lines = [line for line in str(response).split('\n') if '%' in line]
                
                if hot_lines:
                    return [TextContent(type="text", text='\n'.join(hot_lines))]
                else:
                    return [TextContent(type="text", text="No hot threads detected in the cluster.")]
            except Exception as e:
                self.logger.error(f"Error fetching hot threads: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        @mcp.tool(description="Get current tasks in cluster")
        async def get_tasks() -> list[TextContent]:
            """
            Get current tasks running in the cluster.
            Filters duplicate task types to show only unique operations.
            """
            self.logger.info("Fetching cluster tasks...")
            try:
                response = self.es_client.cat.tasks(v=True)
                lines = response.split('\n')
                seen_tasks = set()
                filtered_lines = []
                
                for line in lines:
                    if not line.strip():
                        continue
                    task_type = line.split()[0]
                    if task_type not in seen_tasks:
                        seen_tasks.add(task_type)
                        filtered_lines.append(line)
                        
                if filtered_lines:
                    return [TextContent(type="text", text='\n'.join(filtered_lines))]
                else:
                    return [TextContent(type="text", text="No tasks currently running in the cluster.")]
            except Exception as e:
                self.logger.error(f"Error fetching tasks: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        @mcp.tool(description="Get recovery status and estimated completion time")
        async def get_recovery_status() -> list[TextContent]:
            """
            Get recovery status for shards that are currently being recovered.
            Includes progress percentage and estimated time remaining based on current recovery rate.
            """
            self.logger.info("Fetching recovery status...")
            try:
                # Get active recoveries with detailed stats
                response = self.es_client.cat.recovery(format='json', active_only=True, v=True)
                
                if not response:
                    # Get cluster health to show overall shard status if no active recoveries
                    health = self.es_client.cluster.health()
                    total_shards = health['active_shards'] + health['unassigned_shards'] + health['initializing_shards']
                    active_pct = (health['active_shards'] / total_shards) * 100 if total_shards > 0 else 100
                    
                    status_msg = (
                        f"No active recoveries. Cluster status: {health['status']}\n"
                        f"Active shards: {health['active_shards']}/{total_shards} ({active_pct:.1f}%)\n"
                        f"Initializing: {health['initializing_shards']}\n"
                        f"Unassigned: {health['unassigned_shards']}"
                    )
                    return [TextContent(type="text", text=status_msg)]

                # Process active recoveries
                summary = []
                for recovery in response:
                    index = recovery['index']
                    shard = recovery['shard']
                    stage = recovery.get('stage', 'unknown')
                    
                    # Calculate progress and time remaining
                    files_pct = float(recovery.get('files_percent', '0').rstrip('%'))
                    bytes_pct = float(recovery.get('bytes_percent', '0').rstrip('%'))
                    total_bytes = int(recovery.get('total_bytes', 0))
                    bytes_recovered = int(recovery.get('recovered_in_bytes', 0))
                    
                    # Parse time value which can be in format like "1.2s" or "3m" or "2.5h"
                    time_str = recovery.get('time', '0s')
                    try:
                        # Convert time string to milliseconds
                        if time_str.endswith('ms'):
                            time_spent_ms = float(time_str[:-2])
                        elif time_str.endswith('s'):
                            time_spent_ms = float(time_str[:-1]) * 1000
                        elif time_str.endswith('m'):
                            time_spent_ms = float(time_str[:-1]) * 60 * 1000
                        elif time_str.endswith('h'):
                            time_spent_ms = float(time_str[:-1]) * 60 * 60 * 1000
                        else:
                            time_spent_ms = 0
                    except ValueError:
                        time_spent_ms = 0
                    
                    # Calculate recovery rate and estimated time remaining
                    if bytes_recovered > 0 and time_spent_ms > 0:
                        rate_mb_sec = (bytes_recovered / 1024 / 1024) / (time_spent_ms / 1000)
                        remaining_bytes = total_bytes - bytes_recovered
                        est_seconds_remaining = (remaining_bytes / 1024 / 1024) / rate_mb_sec if rate_mb_sec > 0 else 0
                        
                        # Format time remaining in a human-readable way
                        if est_seconds_remaining < 60:
                            time_remaining = f"{est_seconds_remaining:.0f} seconds"
                        elif est_seconds_remaining < 3600:
                            time_remaining = f"{est_seconds_remaining/60:.1f} minutes"
                        else:
                            time_remaining = f"{est_seconds_remaining/3600:.1f} hours"
                        
                        recovery_info = (
                            f"Index: {index}, Shard: {shard}\n"
                            f"Stage: {stage}\n"
                            f"Progress: files={files_pct:.1f}%, bytes={bytes_pct:.1f}%\n"
                            f"Rate: {rate_mb_sec:.1f} MB/sec\n"
                            f"Est. time remaining: {time_remaining}\n"
                        )
                    else:
                        recovery_info = (
                            f"Index: {index}, Shard: {shard}\n"
                            f"Stage: {stage}\n"
                            f"Progress: files={files_pct:.1f}%, bytes={bytes_pct:.1f}%\n"
                            "Rate: calculating...\n"
                        )
                    
                    summary.append(recovery_info)
                
                return [TextContent(type="text", text="\n".join(summary))]
                
            except Exception as e:
                self.logger.error(f"Error fetching recovery status: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

