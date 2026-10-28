"""initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-28 22:20:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. repositories
    op.create_table(
        'repositories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('owner', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('full_name', sa.String(length=205), nullable=False),
        sa.Column('default_branch', sa.String(length=100), server_default='main', nullable=False),
        sa.Column('is_private', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('html_url', sa.String(length=500), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_repositories_id'), 'repositories', ['id'], unique=False)
    op.create_index(op.f('ix_repositories_owner'), 'repositories', ['owner'], unique=False)
    op.create_index(op.f('ix_repositories_name'), 'repositories', ['name'], unique=False)
    op.create_index(op.f('ix_repositories_full_name'), 'repositories', ['full_name'], unique=True)

    # 2. pull_requests
    op.create_table(
        'pull_requests',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('repository_id', sa.Integer(), nullable=False),
        sa.Column('number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('state', sa.String(length=50), server_default='open', nullable=False),
        sa.Column('author', sa.String(length=100), nullable=False),
        sa.Column('base_sha', sa.String(length=64), nullable=False),
        sa.Column('head_sha', sa.String(length=64), nullable=False),
        sa.Column('html_url', sa.String(length=500), nullable=False),
        sa.Column('diff_url', sa.String(length=500), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('repository_id', 'number', name='uq_repo_pr_number')
    )
    op.create_index(op.f('ix_pull_requests_id'), 'pull_requests', ['id'], unique=False)
    op.create_index(op.f('ix_pull_requests_repository_id'), 'pull_requests', ['repository_id'], unique=False)
    op.create_index(op.f('ix_pull_requests_number'), 'pull_requests', ['number'], unique=False)

    # 3. review_jobs
    op.create_table(
        'review_jobs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('pull_request_id', sa.Integer(), nullable=False),
        sa.Column('commit_sha', sa.String(length=64), nullable=False),
        sa.Column('idempotency_key', sa.String(length=128), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='QUEUED', nullable=False),
        sa.Column('mode', sa.String(length=50), server_default='deterministic', nullable=False),
        sa.Column('total_files_analyzed', sa.Integer(), server_default='0', nullable=False),
        sa.Column('total_findings', sa.Integer(), server_default='0', nullable=False),
        sa.Column('summary', sa.Text(), server_default='', nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['pull_request_id'], ['pull_requests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_review_jobs_id'), 'review_jobs', ['id'], unique=False)
    op.create_index(op.f('ix_review_jobs_pull_request_id'), 'review_jobs', ['pull_request_id'], unique=False)
    op.create_index(op.f('ix_review_jobs_commit_sha'), 'review_jobs', ['commit_sha'], unique=False)
    op.create_index(op.f('ix_review_jobs_idempotency_key'), 'review_jobs', ['idempotency_key'], unique=True)
    op.create_index(op.f('ix_review_jobs_status'), 'review_jobs', ['status'], unique=False)

    # 4. findings
    op.create_table(
        'findings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('review_job_id', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('line_start', sa.Integer(), nullable=True),
        sa.Column('line_end', sa.Integer(), nullable=True),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=300), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('evidence', sa.Text(), nullable=True),
        sa.Column('suggested_remediation', sa.Text(), nullable=True),
        sa.Column('detection_source', sa.String(length=50), nullable=False),
        sa.Column('confidence', sa.String(length=50), server_default='high', nullable=False),
        sa.Column('rule_id', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['review_job_id'], ['review_jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_findings_id'), 'findings', ['id'], unique=False)
    op.create_index(op.f('ix_findings_review_job_id'), 'findings', ['review_job_id'], unique=False)
    op.create_index(op.f('ix_findings_file_path'), 'findings', ['file_path'], unique=False)
    op.create_index(op.f('ix_findings_severity'), 'findings', ['severity'], unique=False)
    op.create_index(op.f('ix_findings_category'), 'findings', ['category'], unique=False)
    op.create_index(op.f('ix_findings_rule_id'), 'findings', ['rule_id'], unique=False)

    # 5. review_feedback
    op.create_table(
        'review_feedback',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('finding_id', sa.Integer(), nullable=False),
        sa.Column('feedback_type', sa.String(length=50), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['finding_id'], ['findings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('finding_id', name='uq_feedback_finding')
    )
    op.create_index(op.f('ix_review_feedback_id'), 'review_feedback', ['id'], unique=False)
    op.create_index(op.f('ix_review_feedback_finding_id'), 'review_feedback', ['finding_id'], unique=True)

    # 6. webhook_deliveries
    op.create_table(
        'webhook_deliveries',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('delivery_id', sa.String(length=100), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=True),
        sa.Column('payload_hash', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='processed', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_webhook_deliveries_id'), 'webhook_deliveries', ['id'], unique=False)
    op.create_index(op.f('ix_webhook_deliveries_delivery_id'), 'webhook_deliveries', ['delivery_id'], unique=True)

def downgrade() -> None:
    op.drop_table('webhook_deliveries')
    op.drop_table('review_feedback')
    op.drop_table('findings')
    op.drop_table('review_jobs')
    op.drop_table('pull_requests')
    op.drop_table('repositories')
