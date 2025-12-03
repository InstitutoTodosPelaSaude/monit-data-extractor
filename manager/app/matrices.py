from minio_connection import list_files_in_folder
import os

def list_matrices(minio_client):

    arbo_matrices_info = list_files_in_folder(minio_client, 'public', 'arbo/reports/current/matrices/csv/')
    respat_matrices_info = list_files_in_folder(minio_client, 'public', 'respat/reports/current/matrices/csv/')
    all_matrices = arbo_matrices_info + respat_matrices_info
    minio_base_url = os.getenv("MINIO_BASE_URL", "http://localhost:9000")

    matrices = [
        { 
            'name': matrices_info[0].split('/')[-1],
            'project': 'arbo' if 'arbo' in matrices_info[0] else 'respat',
            'path': matrices_info[0],
            'size': matrices_info[1],
            'last_modified': matrices_info[2],
            'url': f"{minio_base_url}/public/{matrices_info[0]}"
        } for matrices_info in all_matrices
    ]

    return matrices